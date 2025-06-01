from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.exceptions import UserError
import random


class SecurityVehicleExit(models.Model):
    _name = 'osoul.security.vehicle.exit'
    _description = 'Security Vehicle Exit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "permission_code"

    permission_code = fields.Char(string="Permission Code", readonly=True, tracking=True,store=True)
    #Vehicle Info
    vehicle_id = fields.Many2one('transportation.vehicle', string="Vehicle Info")
    license_plate = fields.Char(string="License Plate")
    manufacturer = fields.Char(string='Manufacturer')
    year = fields.Integer(string='Year')
    color = fields.Selection([
        ('white', 'White'),
        ('red', 'Red'),
        ('black', 'Black'),
        ('ashen', 'Ashen')
    ], string='Color')
    # permit_issuer_id = fields.Many2one('res.users', string="Permit Issuer")
    related_employee_id = fields.Many2one('hr.employee', string="Related Employee")
    employment_no_id = fields.Char(string="Employment No")
    department_id = fields.Many2one('hr.department', string="Department")
    driver_id = fields.Many2one('osoul.transportation.driver', string="Assigned Driver")
    emp_id_no = fields.Char(string="Employee ID")
    emp_department_id = fields.Many2one('hr.department', string="Department")
    country_id = fields.Many2one('res.country', string='Nationality')
    # GATE AND TIMING INFORMATION
    entry_gate_id = fields.Many2one(string="Entering Gate", comodel_name="osoul.security.poultry.gates", ondelete="restrict", tracking=True)
    guard_in_entry_id = fields.Many2one(string="Entering Guard", comodel_name="res.users", ondelete="restrict", tracking=True)
    time_in = fields.Datetime(string="Entering Time", readonly=True, tracking=True)
    exit_gate_id = fields.Many2one(string="Exiting Gate", comodel_name="osoul.security.poultry.gates", ondelete="restrict", tracking=True)
    guard_in_exiting_id = fields.Many2one(string="Exiting Guard", comodel_name="res.users", ondelete="restrict", tracking=True)
    time_out = fields.Datetime(string="Exiting Time", readonly=True, tracking=True)
    # time_spent_inside = fields.Char(string="Time Spent Inside", compute="_compute_time_spent_inside", store=True, tracking=True)
    # state = fields.Selection([("draft", "Draft"),
    #                           ("inside_osoul", "Inside Osoul"),
    #                           ("outside_osoul", "Outside Osoul")], string="State", default="draft", tracking=True)

    gate_entry_record = fields.Char(string="Gate Entry Record", readonly=True, tracking=True)

    @api.depends("time_in", "time_out")
    def _compute_time_spent_inside(self):
        for record in self:
            if record.time_in and record.time_out:
                time_in = record.time_in
                time_out = record.time_out
                time_spent = time_out - time_in
                hours = time_spent.seconds // 3600
                minutes = (time_spent.seconds // 60) % 60
                seconds = time_spent.seconds % 60
                record.time_spent_inside = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                record.time_spent_inside = "00:00:00"

    def create(self, vals):
        record = super(SecurityVehicleExit, self).create(vals)
        record.trigger_exit_notification()
        return record

    def trigger_exit_notification(self):
        message = _("Vehicle exit permission has been successfully allowed.")
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Security Vehicle Exit'),
            'res_model': 'osoul.security.vehicle.exit',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',  # Open the form in a new window
        }
        # Send notification
        self.env['bus.bus']._sendone(
            self.env.user.partner_id,  # The notification is sent to the current user
            'simple_notification', {
                'message': message,
                'title': _('Exit Permit'),
                'sticky': True,  # Ensure it stays until the user closes it
                'action': action,  # This action will link to the specific record
            }
        )

    def action_button_outside_osoul(self):
        self.time_out = datetime.now()
        self.guard_in_exiting_id = self.env.user.id
