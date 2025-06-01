from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError
import requests

class OsoulWaterTankerEntry(models.Model):
    _name = 'osoul.water.tanker.entry'
    _description = 'Water Tanker Entry'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "trip_no"

    trip_no = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    owner_id = fields.Many2one(comodel_name="osoul.water.vendor", string="Vendor", required=True, tracking=True, ondelete='restrict')
    vehicle_id = fields.Many2one('osoul.water.tanker', string='Vehicle', required=True, tracking=True, ondelete='restrict')
    driver_id = fields.Many2one('osoul.tanker.driver', string='Driver Name', required=True, tracking=True, ondelete='restrict')
    driver_phone = fields.Char(related='driver_id.phone', string='Driver Phone')

    # ENTRY INFORMATION
    security_emp_in = fields.Many2one(comodel_name='res.users', string='Entering Employee', readonly=True, ondelete="restrict")
    emoployee_id_in = fields.Many2one(related='security_emp_in.employee_id', string="Enter Security", store=True)
    security_phone = fields.Char(string="Phone No", related='emoployee_id_in.mobile_phone')
    entry_time = fields.Datetime(string='Entry Time', readonly=True)
    # EXIT INFORMATION
    security_emp_out = fields.Many2one(comodel_name='res.users', string='Exiting Employee', readonly=True, ondelete="restrict")
    emoployee_id_out = fields.Many2one(related='security_emp_out.employee_id', string="Exit Security", store=True)
    exiting_time = fields.Datetime(string='Exiting Time', readonly=True)

    total_time_inside_company = fields.Char(string='Time Inside Osoul', compute='_compute_total_time_inside', store=True)
    permission = fields.Selection([('not_authorized', 'Not Authorized'), ('authorized_in', 'Authorized In'),
                                   ('authorized_out', 'Authorized Out')], default='not_authorized', readonly=True, tracking=True,)
    state = fields.Selection([('draft', 'Draft'), ('authorization', 'Authorization'),
                              ('permit_enter', 'Permit Enter'), ('inside_osoul', 'Inside Osoul'),
                              ('permit_exit', 'Permit Exit'), ('outside_osoul', 'Outside Osoul')], default='draft', tracking=True,)
    reception_record = fields.Many2one(comodel_name='osoul.water.reception', string='Reception Record')  # Only Relation With Water Reception Class.


    @api.onchange('owner_id')
    def _onchange_owner_id(self):
        self.vehicle_id = False
        self.driver_id = False
        if self.owner_id:
            return {
                'domain': {
                    'vehicle_id': [('status', '=', 'outside_osoul'), ('owner_id', '=', self.owner_id.id)],
                    'driver_id': [('status', '=', 'outside_osoul'), ('vendor_id', '=', self.owner_id.id)],
                }
            }

    def action_waiting_for_permission(self):
        for record in self:
            record.trip_no = self.env['ir.sequence'].next_by_code('trip.sequence') or _('New')
            record.state = "authorization"
            record.security_emp_in = self.env.user
            record.reception_record = record.env['osoul.water.reception'].create({
                'trip_no': record.trip_no,
                'vehicle_id': record.vehicle_id.id,
                'owner_id': record.owner_id.id if record.owner_id else False,
                'driver_id': record.driver_id.id,
                'driver_phone': record.driver_phone,
                'security_guard': record.security_emp_in.id if record.security_emp_in else False,
                'security_phone': record.security_phone,
                'entry_time': record.entry_time,
                'permission': record.permission,
                'state': record.state,
            })

            # Sending WhatsApp notification to all operators
            record._notify_operators_new_tanker(record)

#==========================================================================================================================#
# NOTIFICATION PART
#==========================================================================================================================#
    
    # DISPLAY NOTIFICATION ON SCREEN

    # WHATSAPP NOTIFICATION
    def _notify_operators_new_tanker(self, record):
        operators = self.env['osoul.water.operator'].search([])
        if not operators:
            raise UserError(_("No operators are available to notify."))

        instance_id = "instance103098"
        token = "dm86hbcidw154pdh"
        api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

        message_body = f"""
Hi Operator,

A new tanker trip is waiting for authorization:
- Trip No: {record.trip_no}
- Vendor: {record.owner_id.display_name}
- Vehicle: {record.vehicle_id.display_name}
- Driver: {record.driver_id.display_name}
- Time: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Osoul Water Management.
"""

        for operator in operators:
            if not operator.phone:
                raise UserError(_("Operator %s does not have a phone number defined." % operator.name))

            payload = {
                'token': token,
                'to': operator.phone,
                'body': message_body.strip()
            }

            try:
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code != 200:
                    raise UserError(_("Failed to send WhatsApp message to operator %s. Response: %s") % (operator.name, response.text))
            except requests.RequestException as e:
                raise UserError(_("Error while sending WhatsApp message to operator %s: %s") % (operator.name, str(e)))

#==========================================================================================================================#
# BUTTONS PART
#==========================================================================================================================#

    def action_enter_osoul(self):
        for record in self:
            if record.permission != "authorized_in":
                raise UserError("Need Permission to Access Osoul")
            else:
                record.entry_time = fields.Datetime.now()
                record.security_emp_in = self.env.user
                record.state = 'inside_osoul'
                record.driver_id.status = "inside_osoul"
                record.vehicle_id.status = "inside_osoul"

            inside_osoul = self.env['osoul.water.reception'].search([('trip_no', '=', record.trip_no)], limit=1)
            if inside_osoul:
                inside_osoul.write({
                    'entry_time': record.entry_time,
                    'state': 'inside_osoul',
                })

            # Notify operators about tanker entry
            self._notify_operators_tanker_entry(record)

    def _notify_operators_tanker_entry(self, record):
        operators = self.env['osoul.water.operator'].search([])
        if not operators:
            raise UserError(_("No operators are available to notify."))

        instance_id = "instance103098"
        token = "dm86hbcidw154pdh"
        api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

        message_body = f"""
Hi Operator,

The tanker has entered the facility with the following details:

- Trip No: {record.trip_no}
- Vendor: {record.owner_id.display_name}
- Vehicle: {record.vehicle_id.display_name}
- Driver: {record.driver_id.display_name}
- Time: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Osoul Water Management.
"""

        for operator in operators:
            if not operator.phone:
                raise UserError(_("Operator %s does not have a phone number defined." % operator.name))

            payload = {
                'token': token,
                'to': operator.phone,
                'body': message_body.strip()
            }

            try:
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code != 200:
                    raise UserError(_("Failed to send WhatsApp message to operator %s. Response: %s") % (operator.name, response.text))
            except requests.RequestException as e:
                raise UserError(_("Error while sending WhatsApp message to operator %s: %s") % (operator.name, str(e)))

    def action_exit_osoul(self):
        for record in self:
            if record.permission != "authorized_out":
                raise UserError("Need Permission to Exit Osoul")
            else:
                record.exiting_time = fields.Datetime.now()
                record.security_emp_out = self.env.user
                record.state = 'outside_osoul'
                record.driver_id.status = "outside_osoul"
                record.vehicle_id.status = "outside_osoul"

            outside_osoul = self.env['osoul.water.reception'].search([('trip_no', '=', record.trip_no)], limit=1)
            if outside_osoul:
                outside_osoul.write({
                    'state': 'outside_osoul'
                })

    @api.depends('entry_time', 'exiting_time')
    def _compute_total_time_inside(self):
        for record in self:
            if record.entry_time and record.exiting_time:
                delta = record.exiting_time - record.entry_time
                total_seconds = int(delta.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                record.total_time_inside_company = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                record.total_time_inside_company = "00:00:00"