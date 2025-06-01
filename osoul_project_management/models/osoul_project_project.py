from datetime import timedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OsoulProject(models.Model):
    _name = 'osoul.project'
    _description = 'Osoul Project'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "project_id"

    # Basic Information
    name = fields.Char(string="Project Name", required=True, tracking=True)
    project_id = fields.Char(string="Project Code", required=True, copy=False, readonly=True, default=lambda self: _('New'))
    description = fields.Text(string="Description", tracking=True)
    start_date = fields.Date(string="Start Date", tracking=True)
    end_date = fields.Date(string="End Date", tracking=True)
    project_duration = fields.Integer(string="Project Duration", compute="_compute_project_duration", store=True, readonly=True)
    remaining_days = fields.Integer(string="Remaining Days", compute="_compute_remaining_days", readonly=True, store=True)
    expected_cost = fields.Float(string="Expected Cost", tracking=True)
    actual_cost = fields.Float(string="Actual Cost", compute="_compute_actual_cost", store=True, readonly=True)
    image = fields.Image(string="Project Image", max_width=1024, max_height=1024)
    state = fields.Selection([('draft', 'Draft'),
                              ('in_progress', 'In Progress'),
                              ('completed', 'Completed'),
                              ('cancelled', 'Cancelled')], default='draft', tracking=True, string="State")
    
    # Relationships
    project_owner = fields.Many2one('hr.employee', string="Project Owner", tracking=True)
    project_manager = fields.Many2one('hr.employee', string="Project Manager", tracking=True)
    task_ids = fields.One2many('osoul.task', 'project_id', string="Tasks", auto_join=True)
    milestone_ids = fields.One2many('osoul.milestone', 'project_id', string="Milestones", auto_join=True)
    expense_ids = fields.One2many('osoul.project.expense', 'project_id', string="Expenses")
    contract_ids = fields.One2many('osoul.contract', 'project_id', string="Contracts")
    quotation_ids = fields.One2many('osoul.quotation', 'project_id', string="Quotations")
    risk_ids = fields.One2many('osoul.project.risk', 'project_id', string="Risk and Challenges")
    
    # Statistics
    total_tasks = fields.Integer(string="Total Tasks", compute="_compute_totals", store=True)
    total_milestones = fields.Integer(string="Total Milestones", compute="_compute_totals", store=True)
    total_expenses = fields.Integer(string="Total Expenses", compute="_compute_totals", store=True)
    total_contracts = fields.Integer(string="Total Contracts", compute="_compute_totals", store=True)
    total_quotations = fields.Integer(string="Total Quotations", compute="_compute_totals", store=True)
    completion_percentage = fields.Float(string="Completion %", compute="_compute_completion_percentage", store=True, readonly=True)

    # Project Team
    team_members_ids = fields.Many2many('hr.employee', string="Team Members", tracking=True)

    # Compute Methods
    @api.depends('start_date', 'end_date')
    def _compute_project_duration(self):
        """Compute the duration of the project based on start_date and end_date."""
        for record in self:
            if record.start_date and record.end_date:
                duration = (record.end_date - record.start_date).days
                record.project_duration = max(duration, 0)  # Ensure no negative durations
            else:
                record.project_duration = 0

    @api.depends('end_date')
    def _compute_remaining_days(self):
        """Compute remaining days until the project's end date."""
        for record in self:
            if record.end_date:
                record.remaining_days = (record.end_date - fields.Date.today()).days
            else:
                record.remaining_days = 0

    @api.depends('expense_ids.amount')
    def _compute_actual_cost(self):
        """Compute the total expenses."""
        for record in self:
            record.actual_cost = sum(expense.amount for expense in record.expense_ids)

    @api.depends('task_ids.state')
    def _compute_completion_percentage(self):
        """Compute the percentage of completed tasks."""
        for record in self:
            total_tasks = len(record.task_ids)
            if total_tasks > 0:
                completed_tasks = len(record.task_ids.filtered(lambda task: task.state == 'complete'))
                record.completion_percentage = (completed_tasks / total_tasks) * 100
            else:
                record.completion_percentage = 0.0

    @api.depends('task_ids', 'milestone_ids', 'expense_ids', 'contract_ids', 'quotation_ids')
    def _compute_totals(self):
        """Compute totals for tasks, milestones, expenses, contracts, and quotations."""
        for record in self:
            record.total_tasks = len(record.task_ids)
            record.total_milestones = len(record.milestone_ids)
            record.total_expenses = len(record.expense_ids)
            record.total_contracts = len(record.contract_ids)
            record.total_quotations = len(record.quotation_ids)

    # ACTION BUTTONS 
    def action_in_progress(self):
        """Start the project."""
        for record in self:
            if record.expected_cost == 0:
                raise ValidationError(_("Set the expected cost before starting the project."))
            record.state = 'in_progress'

    def action_complete(self):
        """Mark the project as completed."""
        for record in self:
            if record.completion_percentage != 100:
                raise ValidationError(_("Project is not ready yet to be completed."))
            record.state = 'completed'

    def action_cancel(self):
        """Cancel the project."""
        for record in self:
            if record.state == 'completed':
                raise ValidationError(_("Completed projects cannot be cancelled."))
            record.state = 'cancelled'

    def action_total_tasks(self):
        """Redirect to the list of tasks associated with this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Tasks'),
            'view_mode': 'tree,form',
            'res_model': 'osoul.task',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_total_milestones(self):
        """Redirect to the list of milestones associated with this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Milestones'),
            'view_mode': 'tree,form',
            'res_model': 'osoul.milestone',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_total_expenses(self):
        """Redirect to the list of expenses associated with this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Expenses'),
            'view_mode': 'tree,form',
            'res_model': 'osoul.project.expense',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_total_contracts(self):
        """Redirect to the list of contracts associated with this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Contracts'),
            'view_mode': 'tree,form',
            'res_model': 'osoul.contract',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    def action_total_quotations(self):
        """Redirect to the list of quotations associated with this project."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Quotations'),
            'view_mode': 'tree,form',
            'res_model': 'osoul.quotation',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id},
        }

    # Cron Jobs
    def update_daily_fields(self):
        for project in self.search([]):
            project._compute_remaining_days()
            project._compute_completion_percentage()

    @api.model
    def create(self, vals):
        if vals.get('project_id', _('New')) == _('New'):
            vals['project_id'] = self.env['ir.sequence'].next_by_code('osoul.project') or _('New')
        return super(OsoulProject, self).create(vals)