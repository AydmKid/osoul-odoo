from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import requests

class OsoulBuffetOrder(models.Model):
    _name = 'osoul.buffet.order'
    _description = 'Buffet Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Order ID", readonly=True)
    customer = fields.Many2one(comodel_name="res.users", string="Customer", default=lambda self: self.env.user, readonly=True)
    phone = fields.Char(string="Customer Phone", related='customer.employee_id.mobile_phone', readonly=True)
    order_submitted = fields.Datetime(string="Order Date", readonly=True)
    order_accepted = fields.Datetime(string="Order Accepted", readonly=True)
    accept_duration = fields.Char(string="Accept Duration", compute="_compute_accept_duration")
    order_delivered = fields.Datetime(string="Order Delivered", readonly=True)
    order_duration = fields.Char(string="Order Duration", compute="_compute_order_duration")
    order_line_ids = fields.One2many('osoul.buffet.order.line', 'order_id', string="Order Lines")
    operator_ids = fields.Many2many('osoul.buffet.operator', string="Assigned Operators", required=True,
                                                             default=lambda self: self._default_operators())
    category_id = fields.Many2one(string="Category", related='order_line_ids.category_id')
    subcategory_id = fields.Many2one(string="Subcategory", related='order_line_ids.subcategory_id')
    stock_id = fields.Many2one(string="Item", related='order_line_ids.stock_id')
    quantity = fields.Integer(string="Quantity", related='order_line_ids.quantity')
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'),
                              ('preparing', 'Preparing'), ('delivered', 'Delivered'),
                              ('canceled', 'Canceled')], default="draft", readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('osoul.buffet.order') or _('New')
        return super(OsoulBuffetOrder, self).create(vals)
    
    @api.model
    def _default_operators(self):
        """ Fetch all buffet operators by default. """
        return self.env['osoul.buffet.operator'].search([]).ids
    
    # COMPUTE ORDER ACCEPT DURATION
    @api.depends('order_submitted', 'order_accepted')
    def _compute_accept_duration(self):
        for record in self:
            if record.order_submitted and record.order_accepted:
                duration = record.order_accepted - record.order_submitted
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                record.accept_duration = f"{int(hours)}h {int(minutes)}m"
            else:
                record.accept_duration = "Not Accepted Yet"

    # COMPUTE ORDER DURATION TIME TO DELIVERED
    @api.depends('order_submitted', 'order_delivered')
    def _compute_order_duration(self):
        for record in self:
            if record.order_submitted and record.order_delivered:
                duration = record.order_delivered - record.order_submitted
                hours, remainder = divmod(duration.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                record.order_duration = f"{int(hours)}h {int(minutes)}m"
            else:
                record.order_duration = "Not Delivered Yet"

    # SUBMITTING ORDER BUTTON
    def action_order_submitted(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("Only draft orders can be submitted."))
            if not record.order_line_ids:
                raise ValidationError(_("You cannot submit an order without any order lines."))

            # Check stock availability and reduce stock
            for line in record.order_line_ids:
                if line.quantity > line.stock_id.quantity:
                    raise ValidationError(_("Not enough stock for item '%s'. Available: %s, Ordered: %s") %
                                          (line.stock_id.name, line.stock_id.quantity, line.quantity))
                # Reduce stock quantity
                line.stock_id.quantity -= line.quantity

                # Record stock movement
                self.env['buffet.stock.movement'].create({
                    'stock_id': line.stock_id.id,
                    'quantity_change': -line.quantity,
                    'reason': _("Order submitted: %s" % record.name),
                    'user_id': self.env.user.id,
                })
            record.order_submitted = fields.Datetime.now()
            record.state = 'submitted'
            record.message_post(body=_("Order has been submitted successfully!"))
            record.submit_whatsapp_message()

    # PREPRING ORDER BUTTON
    def action_order_accepted(self):
        for record in self:
            if record.state != 'submitted':
                raise ValidationError(_("Only submitted orders can be marked as preparing."))
            record.state = 'preparing'
            record.order_accepted = fields.Datetime.now()
            record.message_post(body=_("Order is now being prepared."))
            record.preparing_whatsapp_message()

    # DELIVRY ORDER NUTTON
    def action_order_delivered(self):
        for record in self:
            if record.state != 'preparing':
                raise ValidationError(_("Only orders in preparation can be marked as delivered."))
            record.state = 'delivered'
            record.order_delivered = fields.Datetime.now()
            record.message_post(body=_("Order has been delivered."))
            record.delivered_whatsapp_message()

    # CANCEL ORDER BUTTON
    def action_cancel_order(self):
        for record in self:
            if record.state == 'delivered':
                raise ValidationError(_("Delivered orders cannot be canceled."))
            for line in record.order_line_ids:
                line.stock_id.quantity += line.quantity
                self.env['buffet.stock.movement'].create({
                    'stock_id': line.stock_id.id,
                    'quantity_change': line.quantity,
                    'reason': _("Order canceled: %s" % record.name),
                    'user_id': self.env.user.id,
                })
            record.state = 'canceled'
            record.message_post(body=_("Order has been canceled."))

    # WHATSAPP SUBMITTING ORDER BUTTON
    def submit_whatsapp_message(self):
        for record in self:
            if not record.operator_ids:
                raise ValidationError(_("No operators have been assigned to this order."))

            instance_id = "instance103098"
            token = "dm86hbcidw154pdh"
            api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            order_lines_text = "\n".join([f"- {line.quantity} x {line.stock_id.name}" for line in record.order_line_ids])

            for operator in record.operator_ids:
                # Access the phone number correctly
                if not operator.name.mobile_phone:
                    raise ValidationError(_("Operator %s does not have a phone number defined.") % operator.name.name)

                message_body = f""" Hi {operator.name.mobile_phone},
                
New Order Submitted
- Order: {record.name} 
- Customer: {record.customer.name}
- Time: {record.order_submitted.strftime('%Y-%m-%d %H:%M:%S')}
- Items: {order_lines_text}
"""

                payload = {
                    'token': token,
                    'to': operator.name.mobile_phone,
                    'body': message_body.strip()
                }

                try:
                    response = requests.post(api_url, json=payload, timeout=10)
                    if response.status_code != 200:
                        raise ValidationError(_("Failed to send WhatsApp message to operator %s. Response: %s") % (operator.name.name, response.text))
                except requests.RequestException as e:
                    raise ValidationError(_("Error while sending WhatsApp message to operator %s: %s") % (operator.name.name, str(e)))


    # WHATSAPP PREPARING ORDER BUTTON      
    def preparing_whatsapp_message(self):
        for record in self:
            if not record.phone:
                raise ValidationError(_("Customer phone number is not defined."))

            instance_id = "instance103098"
            token = "dm86hbcidw154pdh"
            api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            order_lines_text = "\n".join([f"- {line.quantity} x {line.stock_id.name}" for line in record.order_line_ids])

            message_body = f""" Hi {record.customer.employee_id.mobile_phone},

            We Preparing Your Order.
            - Order: {record.name}
            - Time: {record.order_accepted.strftime('%Y-%m-%d %H:%M:%S')}
            - Items: {order_lines_text}
            """

            payload = {
                'token': token,
                'to': record.phone,
                'body': message_body.strip()
            }

            try:
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code != 200:
                    raise ValidationError(_("Failed to send WhatsApp message to customer. Response: %s") % response.text)
            except requests.RequestException as e:
                raise ValidationError(_("Error while sending WhatsApp message to customer: %s") % str(e))
            

    # WHATSAPP DELIVERY ORDER BUTTON
    def delivered_whatsapp_message(self):
        for record in self:
            if not record.phone:
                raise ValidationError(_("Customer phone number is not defined."))

            # WhatsApp API details
            instance_id = "instance103098"
            token = "dm86hbcidw154pdh"
            api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            # Construct WhatsApp message body
            order_lines_text = "\n".join([f"- {line.quantity} x {line.stock_id.name}" for line in record.order_line_ids])

            message_body = f""" Hi {record.customer.employee_id.mobile_phone},

            You Odred Has Been Delivered
            - Order: {record.name}
            - Time: {record.order_delivered.strftime('%Y-%m-%d %H:%M:%S')}
            - Items: {order_lines_text}
            - A.Duration: {record.accept_duration}
            - O.Duration: {record.order_duration}
            """

            payload = {
                'token': token,
                'to': record.phone,
                'body': message_body.strip()
            }

            try:
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code != 200:
                    raise ValidationError(_("Failed to send WhatsApp message to customer. Response: %s") % response.text)
            except requests.RequestException as e:
                raise ValidationError(_("Error while sending WhatsApp message to customer: %s") % str(e))


class OsoulBuffetOrderLine(models.Model):
    _name = 'osoul.buffet.order.line'
    _description = 'Buffet Order Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Order ID", related='order_id.name', readonly=True)
    category_id = fields.Many2one(comodel_name="osoul.buffet.category", string="Category", required=True)
    subcategory_id = fields.Many2one(comodel_name="osoul.buffet.subcategory", string="Subcategory", domain="[('category_id', '=', category_id)]", required=True)
    stock_id = fields.Many2one(comodel_name="osoul.buffet.stock", string="Item", domain="[('subcategory_id', '=', subcategory_id)]", required=True)
    extra_ids = fields.Many2many('osoul.buffet.options', string="Exrta")
    stock_qty = fields.Integer(string="Stock", related='stock_id.quantity', readonly=True)
    quantity = fields.Integer(string="Quantity", default=1, required=True)
    order_id = fields.Many2one(comodel_name="osoul.buffet.order", string="Order Reference", required=True)

    @api.onchange('category_id')
    def _onchange_category_id(self):
        self.subcategory_id = False
        self.stock_id = False

    @api.onchange('subcategory_id')
    def _onchange_subcategory_id(self):
        self.stock_id = False

    @api.constrains('quantity')
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_("Quantity must be greater than zero."))
            if record.quantity > record.stock_qty:
                raise ValidationError(_("Ordered quantity exceeds available stock."))
            

class OsoulBuffetOptions(models.Model):
    _name = 'osoul.buffet.options'
    _description = ''
    _rec_name = ''

    name = fields.Char(string="Options", readonly=True)