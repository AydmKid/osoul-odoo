from odoo import models, fields, api, _

class OsoulMilestone(models.Model):
    _name = 'osoul.milestone'
    _description = 'Osoul Milestone'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char(string="Milestone Name", required=True, translate=True)
    project_id = fields.Many2one('osoul.project', string="Project", ondelete='cascade', readonly=True)
    start_date = fields.Date(string="Start Date", help="The start date of the milestone.")
    deadline = fields.Date(string="Deadline")
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'In Progress'),
                              ('complete', 'Complete')], default="draft", string="State", tracking=True, readonly=True)
    
    task_ids = fields.One2many('osoul.task', 'milestone_id', string="Tasks")
    total_tasks = fields.Integer(string="Total Tasks", compute="_compute_task_stats", store=True)
    completed_task_percentage = fields.Float(string="Completed Task (%)", compute="_compute_task_stats", store=True)

    @api.depends('task_ids.state')
    def _compute_task_stats(self):
        for record in self:
            total = len(record.task_ids)
            completed = len(record.task_ids.filtered(lambda task: task.state == 'complete'))
            record.total_tasks = total
            record.completed_task_percentage = (completed / total * 100) if total > 0 else 0.0

    @api.constrains('start_date', 'deadline')
    def _check_dates_within_project(self):
        for record in self:
            if record.start_date and record.project_id.start_date and record.start_date < record.project_id.start_date:
                raise models.ValidationError(_("The milestone's start date cannot be before the project's start date."))
            if record.deadline and record.project_id.end_date and record.deadline > record.project_id.end_date:
                raise models.ValidationError(_("The milestone's deadline cannot be after the project's end date."))
            if record.start_date and record.deadline and record.start_date > record.deadline:
                raise models.ValidationError(_("The milestone's start date cannot be after its deadline."))

    def action_state_progress(self):
        for record in self:
            if record.state == 'draft':
                record.state = "in_progress"
            else:
                raise models.UserError(_("State can only be set to 'In Progress' from 'Draft'."))

    def action_state_complete(self):
        for record in self:
            if record.state == 'in_progress':
                record.state = "complete"
            else:
                raise models.UserError(_("State can only be set to 'Complete' from 'In Progress'."))