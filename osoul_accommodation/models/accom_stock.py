import logging
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import date

# Set up logger
_logger = logging.getLogger(__name__)

class AccommodationStock(models.Model):
    _name = 'osoul.accommodation.stock'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_name'

    permission_code = fields.Char(string="Code", readonly=True, tracking=True)
    image = fields.Binary(string="Item Image", attachment=True)
    product_name = fields.Char(string="Product Name", required=True)
    quantity = fields.Integer(string="Quantity", default=0)
    quantity_spent = fields.Integer(string="Quantity Spent", readonly=True, default=0)
    color = fields.Integer(string="Color Index")  # Adding a color field
    current_date = fields.Datetime(string="Date of Receipt",default=fields.Datetime.now())
    
    product_useage= fields.Selection([
        ('general', 'General'),
        ('personal', 'Personal')
    ], string="Usage")  # Adding usage field

    product_size= fields.Selection([
        ('small', 'Small'),
        ('big', 'Big')
    ], string="Size")  # Adding size field

    product_type= fields.Selection([
        ('liter', 'Liter'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('bit', 'bit')
    ], string="Type")  # Adding type field
    
    # AUTO RECORD CODING SYSTEM
    @api.model
    def create(self, vals):
        if vals.get('permission_code', 'New') == 'New':
            vals['permission_code'] = self.env['ir.sequence'].next_by_code('accommodation_stock_sequence') or 'New'
        return super(AccommodationStock, self).create(vals)

    _sql_constraints = [
        ('product_name_unique', 'unique(product_name)', 'The product name must be unique.')
    ]

    @api.constrains('quantity')
    def _check_quantity_non_zero(self):
        for record in self:
            if record.quantity < 0:
                raise ValidationError(
                    _('The quantity for %s must be greater than zero.') % record.product_name
                )

    def decrease_stock_quantity(self, quantity):
        for stock in self:
            if stock.quantity < quantity:
                raise ValidationError(
                    _('Stock for %s is insufficient!') % stock.product_name
                )
            _logger.info(f'Updating stock: {stock.product_name}, Decreasing quantity by: {quantity}')
            stock.write({
                'quantity': stock.quantity - quantity,
                'quantity_spent': stock.quantity_spent + quantity
            })
            _logger.info(f'New quantity: {stock.quantity}, New quantity_spent: {stock.quantity_spent}')


class AccommodationLogLineStockEmp(models.Model):
    _name = 'osoul.accommodation.log.line.stock.emp'
    _description = 'Accommodation Log Line'

    log_id = fields.Many2one('osoul.accommodation.log', string="Log", required=True, ondelete='cascade')
    stock_id = fields.Many2one(
        'osoul.accommodation.stock', 
        string="Stock Item", 
        required=True,
        
    )
    quantity_used = fields.Integer(string="Quantity Used", required=True, default=1)
    available_quantity = fields.Integer(related='stock_id.quantity', string="Available Quantity", readonly=True)
    current_date = fields.Datetime(string="Date of Receipt",default=fields.Datetime.now())
    

    @api.constrains('quantity_used')
    def _check_stock_quantity(self):
        for line in self:
            product_name = line.stock_id.product_name or 'Unknown Product'
            quantity_available = line.stock_id.quantity

            if line.quantity_used > quantity_available:
                raise ValidationError(
                    _('Not enough stock for {}! Only {} available.').format(
                        product_name, quantity_available
                    )
                )

    @api.model
    def create(self, vals):
        record = super(AccommodationLogLineStockEmp, self).create(vals)
        record.stock_id.decrease_stock_quantity(record.quantity_used)
        if record.stock_id.quantity == 5:
            record.action_notification()
        return record

    def write(self, vals):
        original_quantity = self.quantity_used
        result = super(AccommodationLogLineStockEmp, self).write(vals)
        new_quantity = vals.get('quantity_used', original_quantity)
        difference = new_quantity - original_quantity
        if difference != 0:
            self.stock_id.decrease_stock_quantity(difference)
            if self.stock_id.quantity == 5:
                self.action_notification()
        return result

    def _decrease_stock_quantity(self, quantity_difference=None):
        for line in self:
            quantity_difference = quantity_difference or line.quantity_used
            stock = line.stock_id

            if stock.quantity < quantity_difference:
                raise ValidationError(
                    _('Stock for {} is insufficient!').format(stock.product_name)
                )

            # Decrease stock quantity
            stock.quantity -= quantity_difference

    @api.model
    def action_notification(self):
        message = "Stock quantity is 5"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'danger',
                'sticky': True,
            }
        }
               

class AccommodationLogLineStockRoom(models.Model):
    _name = 'osoul.accommodation.log.line.stock.room'
    _description = 'Accommodation Log Line room'

    
    logs_ids = fields.Many2one('osoul.accommodation.room', string="Log", required=True, ondelete='cascade')
    stock_id = fields.Many2one(
        'osoul.accommodation.stock', 
        string="Stock Item", 
        required=True,
        domain=[('product_useage', '=', 'general')]  # Filter by 'general'
    )
    quantity_used = fields.Integer(string="Quantity Used", required=True, default=1)
    available_quantity = fields.Integer(related='stock_id.quantity', string="Available Quantity", readonly=True)
    current_date = fields.Datetime(string="Date of Receipt",default=fields.Datetime.now())

    @api.constrains('quantity_used')
    def _check_stock_quantity(self):
        for line in self:
            product_name = line.stock_id.product_name or 'Unknown Product'
            quantity_available = line.stock_id.quantity

            if line.quantity_used > quantity_available:
                raise ValidationError(
                    _('Not enough stock for {}! Only {} available.').format(
                        product_name, quantity_available
                    )
                )

    @api.model
    def create(self, vals):
        record = super(AccommodationLogLineStockRoom, self).create(vals)
        record._decrease_stock_quantity()
        return record

    def write(self, vals):
        original_quantity = self.quantity_used
        result = super(AccommodationLogLineStockRoom, self).write(vals)
        new_quantity = vals.get('quantity_used', original_quantity)
        difference = new_quantity - original_quantity
        if difference != 0:
            self._decrease_stock_quantity(difference)
        return result

    def _decrease_stock_quantity(self, quantity_difference=None):
        for line in self:
            quantity_difference = quantity_difference or line.quantity_used
            stock = line.stock_id

            if stock.quantity < quantity_difference:
                raise ValidationError(
                    _('Stock for {} is insufficient!').format(stock.product_name)
                )

            # Decrease stock quantity and update quantity_spent
            stock.write({
                'quantity': stock.quantity - quantity_difference,
                'quantity_spent': stock.quantity_spent + quantity_difference
            })


    @api.model
    def action_notification(self):
        message = "Stock quantity is 5"
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'danger',
                'sticky': True,
            }
        }

class AccommodationLogLineStockApartment(models.Model):
    _name = 'osoul.accommodation.log.line.stock.apartment'
    _description = 'Accommodation Log Line stock apartment'

        
    logs_ids = fields.Many2one('osoul.accommodation.apartment', string="Log", required=True, ondelete='cascade')
    stock_id = fields.Many2one(
        'osoul.accommodation.stock', 
        string="Stock Item", 
        required=True,
        domain=[('product_useage', '=', 'general')]  # Filter by 'general'
    )
    quantity_used = fields.Integer(string="Quantity Used", required=True, default=1)
    available_quantity = fields.Integer(related='stock_id.quantity', string="Available Quantity", readonly=True)
    current_date = fields.Datetime(string="Date of Receipt",default=fields.Datetime.now())

    @api.constrains('quantity_used')
    def _check_stock_quantity(self):
        for line in self:
            product_name = line.stock_id.product_name or 'Unknown Product'
            quantity_available = line.stock_id.quantity

            if line.quantity_used > quantity_available:
                raise ValidationError(
                    _('Not enough stock for {}! Only {} available.').format(
                        product_name, quantity_available
                    )
                )

    @api.model
    def create(self, vals):
        record = super(AccommodationLogLineStockApartment, self).create(vals)
        record._decrease_stock_quantity()
        return record

    def write(self, vals):
        original_quantity = self.quantity_used
        result = super(AccommodationLogLineStockApartment, self).write(vals)
        new_quantity = vals.get('quantity_used', original_quantity)
        difference = new_quantity - original_quantity
        if difference != 0:
            self._decrease_stock_quantity(difference)
        return result

    def _decrease_stock_quantity(self, quantity_difference=None):
        for line in self:
            quantity_difference = quantity_difference or line.quantity_used
            stock = line.stock_id

            if stock.quantity < quantity_difference:
                raise ValidationError(
                    _('Stock for {} is insufficient!').format(stock.product_name)
                )

            # Decrease stock quantity and update quantity_spent
            stock.write({
                'quantity': stock.quantity - quantity_difference,
                'quantity_spent': stock.quantity_spent + quantity_difference
            })


class AccommodationLogLineStockFloor(models.Model):
    _name = 'osoul.accommodation.log.line.stock.floor'
    _description = 'Accommodation Log Line stock floor'

        
    logs_ids = fields.Many2one('osoul.accommodation.floor', string="Log", required=True, ondelete='cascade')
    stock_id = fields.Many2one(
        'osoul.accommodation.stock', 
        string="Stock Item", 
        required=True,
        domain=[('product_useage', '=', 'general')]  # Filter by 'general'
    )
    quantity_used = fields.Integer(string="Quantity Used", required=True, default=1)
    available_quantity = fields.Integer(related='stock_id.quantity', string="Available Quantity", readonly=True)
    current_date = fields.Datetime(string="Date of Receipt",default=fields.Datetime.now())

    @api.constrains('quantity_used')
    def _check_stock_quantity(self):
        for line in self:
            product_name = line.stock_id.product_name or 'Unknown Product'
            quantity_available = line.stock_id.quantity

            if line.quantity_used > quantity_available:
                raise ValidationError(
                    _('Not enough stock for {}! Only {} available.').format(
                        product_name, quantity_available
                    )
                )

    @api.model
    def create(self, vals):
        record = super(AccommodationLogLineStockFloor, self).create(vals)
        record._decrease_stock_quantity()
        return record

    def write(self, vals):
        original_quantity = self.quantity_used
        result = super(AccommodationLogLineStockFloor, self).write(vals)
        new_quantity = vals.get('quantity_used', original_quantity)
        difference = new_quantity - original_quantity
        if difference != 0:
            self._decrease_stock_quantity(difference)
        return result

    def _decrease_stock_quantity(self, quantity_difference=None):
        for line in self:
            quantity_difference = quantity_difference or line.quantity_used
            stock = line.stock_id

            if stock.quantity < quantity_difference:
                raise ValidationError(
                    _('Stock for {} is insufficient!').format(stock.product_name)
                )

            # Decrease stock quantity and update quantity_spent
            stock.write({
                'quantity': stock.quantity - quantity_difference,
                'quantity_spent': stock.quantity_spent + quantity_difference
            })