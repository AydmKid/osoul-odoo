from odoo import models, fields, api, _
from datetime import datetime

class TicketApproval(models.Model):
    _name = 'ticket.approval'
    _description = 'Ticket Approval'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "job_order_sequence"

    # Fields definitions
    responsible_user = fields.Many2one('res.users', string="Responsible User")
    issue_location_id = fields.Many2one('osoul.tickets.settings', string='Issue Location', required=True, ondelete='restrict', tracking=True)
    permit_issuer_id = fields.Many2one('res.users', string="Permit Issuer", default=lambda self: self.env.user.id, readonly=True, tracking=True)
    job_order_sequence = fields.Char(string='Job Order', readonly=True, copy=False)
    ticket_id = fields.Many2one('ticket.job.order', string='Related Ticket', readonly=True)
    assignees_name = fields.Many2many('osoul.tickets.team.member', string='Technician Assignees', required=True,
                                      domain="[('unit_name', '=', responsible_unit)]")  # Filters based on unit
    description = fields.Text(string='Issue Description', readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Requester Name", ondelete='restrict', readonly=True, tracking=True)
    ticket_date = fields.Datetime(string="Ticket Date", readonly=True)
    employement_no = fields.Char(related='employee_id.employment_no', string="Requester Id", tracking=True)
    requester_no = fields.Char(string="Requester No", tracking=True, readonly=True)
    department = fields.Many2one(related='employee_id.department_id', string="Requester Department", tracking=True, store=True)
    unit_head = fields.Many2one('res.users', string="Unit Head", readonly=True)
    solution = fields.Text(string='Solution')
    hold_reason = fields.Char(string='Hold Reason')
    responsible_unit = fields.Selection([
        ('networks', 'Networks'),
        ('systems', 'Systems'),
        ('technical_support', 'Technical Support'),
        ('developers', 'Developers'),
        ('operation', 'Operation'),
        ('information_technology_office', 'Information Technology Office')
    ], string='Unit Name', readonly=True)
    location = fields.Selection([('osoul_poultry', 'Osoul Poultry'),
                                 ('osoul_hatchery', 'Osoul Hatchery'),
                                 ('osoul_jeddah', 'Osoul Jeddah'),
                                 ('osoul_jizan', 'Osoul Jizan'),
                                 ('osoul_abha', 'Osoul Abha')], string="Site", readonly=True)
    state = fields.Selection([
        ('job_created', 'Job Created'),
        ('canceled', 'Canceled'),
        ('hold', 'Hold'),
        ('under_progress', 'Under Progress'),
        ('done', 'Done'),
    ], default='job_created', string='Status', track_visibility='onchange')

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
        ('urgent', 'Urgent')
    ], default='medium', string='Priority', tracking=True)

    is_readonly_for_user = fields.Boolean(
        string="Is Readonly for User",
        compute='_compute_is_readonly_for_user',
        store=False
    )

    @api.depends('create_uid')
    def _compute_is_readonly_for_user(self):
        readonly_user_ids = []  # Replace with the actual user IDs
        for record in self:
            record.is_readonly_for_user = self.env.user.id in readonly_user_ids

    # Date fields for tracking actions
    approval_date = fields.Datetime(string='Approval Date', default=fields.Datetime.now)
    approved_by = fields.Many2one('res.users', string='Approved By', default=lambda self: self.env.user)
    under_progress_date = fields.Datetime(string='Under Progress Date', readonly=True)
    hold_date = fields.Datetime(string='Hold Date', readonly=True)
    finish_date = fields.Datetime(string='Finish Date', readonly=True)

    time_to_start = fields.Integer(string="Time to Under Progress", compute='_compute_time_to_start', store=True, readonly=True)

    time_difference = fields.Integer(string="Time Taken", compute='_compute_time_difference', store=True, readonly=True)

    @api.depends('ticket_date', 'under_progress_date')
    def _compute_time_to_start(self):
        for record in self:
            if record.ticket_date and record.under_progress_date:
                time_diff = record.under_progress_date - record.ticket_date
                record.time_to_start = int(time_diff.total_seconds() / 60)  # Convert to minutes
            else:
                record.time_to_start = 0

    @api.depends('under_progress_date', 'finish_date')
    def _compute_time_difference(self):
        for record in self:
            if record.under_progress_date and record.finish_date:
                time_diff = record.finish_date - record.under_progress_date
                record.time_difference = int(time_diff.total_seconds() / 60)  # Convert to minutes
            else:
                record.time_difference = 0

    def action_under_progress(self):
        """Set state to 'under_progress', log datetime, and update ticket.job.order."""
        self.state = 'under_progress'
        self.under_progress_date = fields.Datetime.now()
        self._compute_time_to_start()
        if self.ticket_id:
            self.ticket_id.hold_reason = self.hold_reason
            self.ticket_id.under_progress_date = self.under_progress_date
            self.ticket_id.time_to_start = self.time_to_start
            self.ticket_id.state = 'under_progress'
            self.ticket_id.assignees_name = [(6, 0, self.assignees_name.ids)]

    def action_hold(self):
        """Set state to 'hold', clear under_progress_date if moving from 'under_progress', and update ticket.job.order."""
        if self.state == 'under_progress':
            self.under_progress_date = False
            if self.ticket_id:
                self.ticket_id.under_progress_date = False
        self.state = 'hold'
        self.hold_date = fields.Datetime.now()
        if self.ticket_id:
            self.ticket_id.hold_date = self.hold_date
            self.ticket_id.state = 'hold'
            self.ticket_id.assignees_name = [(6, 0, self.assignees_name.ids)]

    def action_finish(self):
        """Set state to 'done', log finish datetime, and send time difference to ticket.job.order."""
        self.state = 'done'
        self.finish_date = fields.Datetime.now()
        self._compute_time_difference()
        if self.ticket_id:
            self.ticket_id.finish_date = self.finish_date
            self.ticket_id.time_difference = self.time_difference
            self.ticket_id.state = 'done' 
            self.ticket_id.solution = self.solution
            self.ticket_id.assignees_name = [(6, 0, self.assignees_name.ids)]
        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('Nice Job'),
                'type': 'rainbow_man',
            }
        }
