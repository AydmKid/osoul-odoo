from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.exceptions import UserError
import random


class SecurityEmergencyVisitor(models.Model):
    _name = "osoul.security.emergency.visit"
    _description = ""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "record_no"

    record_no = fields.Char(string="Record No", tracking=True)
    permission_code = fields.Char(string="Permission Code", readonly=True, tracking=True)
    visito_name  = fields.Many2one(comodel_name='res.partner', string='Visitor Name',
                                    domain = ['|',('in_out_state', '=', 'draft'), ('in_out_state', '=', 'outside_osoul')],
                                    ondelete='restrict', tracking=True)
    visitor_name = fields.Many2one(comodel_name='res.partner', string='Visitor Name',
                                    domain = ['|',('in_out_state', '=', 'draft'), ('in_out_state', '=', 'outside_osoul')],
                                    ondelete='restrict', tracking=True)
    position  = fields.Char(string = "Position Name", tracking=True)
    company_name  = fields.Many2one(comodel_name='res.partner', string='Company Name',
                                    domain = ['|',('in_out_state', '=', 'draft'), ('in_out_state', '=', 'outside_osoul')],
                                    ondelete='restrict', tracking=True)
    visitor_type_id = fields.Many2one('osoul.security.visits.types', string='Visit Type')
    purpose  = fields.Text(string="Purpose", tracking=True)
    time_in = fields.Datetime(string="Entering Time", readonly=True, tracking=True)
    time_out = fields.Datetime(string="Exiting Time", readonly=True, tracking=True)
    time_spent_inside = fields.Char(
        string="Time Spent Inside",
        compute="_compute_time_spent_inside",
        store=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("inside_osoul", "Inside Osoul"),
            ("outside_osoul", "Outside Osoul"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )
    entry_gate_id = fields.Many2one(
        string="Entering Gate",
        comodel_name="osoul.security.poultry.gates",
        ondelete="restrict",
        tracking=True,
    )
    guard_in_entry_id = fields.Many2one(
        string="Entering Guard",
        comodel_name="res.users",
        ondelete="restrict",
        tracking=True,
    )
    exit_gate_id = fields.Many2one(
        string="Exiting Gate",
        comodel_name="osoul.security.poultry.gates",
        ondelete="restrict",
        tracking=True,
    )
    guard_in_exiting_id = fields.Many2one(
        string="Exiting Guard",
        comodel_name="res.users",
        ondelete="restrict",
        tracking=True,
    )
    enter_exit_permission = fields.Selection([('draft', 'Draft'),
                                              ('allowed_enter', 'Allowed Enter'),
                                              ('exit_not_allowed', 'Exit Not Allowed'),
                                              ('allowed_exit', 'Allowed Exit'),
                                              ('visitor_out', 'Visitor Out')], default="draft", string="Enter Exit Allowed Visitor", tracking=True)

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

    # RUNNING BUTTON
    def action_running_permission(self):
        self.state = "inside_osoul"
        self.enter_exit_permission = "allowed_enter"

    def action_button_inside_osoul(self):
        self.state = "inside_osoul"
        self.time_in = datetime.now()
        self.guard_in_entry_id = self.env.user.id
        self.record_no = self.env["ir.sequence"].next_by_code(
            "security_emergency_government_visits_sequence"
        )

    def action_button_outside_osoul(self):
        self.state = "outside_osoul"
        self.time_out = datetime.now()
        self.guard_in_exiting_id = self.env.user.id

    @api.model
    def _check_deletion_restrictions(self):
        restricted_states = ['inside_osoul', 'outside_osoul']
        restrict_records = self.filtered(lambda r: r.state in restricted_states)
        if restrict_records:
            raise UserError(_("Deletion of records is not allowed when the state is 'inside_osoul' or 'outside_osoul'."))

    def unlink(self):
        self._check_deletion_restrictions()
        return super(SecurityEmergencyVisitor, self).unlink()