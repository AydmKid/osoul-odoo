from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class OsoulTask(models.Model):
    _name = 'osoul.task'
    _description = 'Osoul Task'

    name = fields.Char(string="Name", required=True, tracking=True)
    description = fields.Text(string="Description", tracking=True)
    start_date = fields.Date(string="Start", tracking=True)
    end_date = fields.Date(string="End", tracking=True)
    task_duration = fields.Integer(string="Duration Days", compute="_compute_task_duration", store=True, readonly=True)
    remaining_days = fields.Integer(string="Remaining Days", compute="_compute_remaining_days", store=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Priority", default='medium', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('complete', 'Complete')
    ], default="draft", tracking=True)
    warning = fields.Selection([
        ('on_plan', 'On Plan'),
        ('approaching_deadline', 'Approaching Deadline'),
        ('late', 'Late')
    ], string="Warning", compute="_compute_warning", store=True)
    progress = fields.Float(string="Progress (%)", default=0.0, tracking=True)
    project_id = fields.Many2one('osoul.project', string="Project", ondelete='cascade', readonly=True)
    milestone_id = fields.Many2one(
        'osoul.milestone',
        string="Milestone",
        ondelete='cascade',
        help="The milestone under which this task falls.",
        required=True,
        domain="[('project_id', '=', project_id)]"
    )
    assigned_employee_id = fields.Many2one(
        'hr.employee',
        string="Assigned Employee",
        help="Select an employee from the assigned project team."
    )

    @api.constrains('start_date', 'end_date', 'milestone_id')
    def _check_task_within_milestone(self):
        for record in self:
            if record.milestone_id:
                milestone_start = record.milestone_id.start_date
                milestone_deadline = record.milestone_id.deadline

                # Ensure task's start_date is not before the milestone's start_date
                if milestone_start and record.start_date and record.start_date < milestone_start:
                    raise ValidationError(
                        _("The task's start date (%s) cannot be before the milestone's start date (%s).")
                        % (record.start_date, milestone_start)
                    )

                # Ensure task's end_date is not after the milestone's deadline
                if milestone_deadline and record.end_date and record.end_date > milestone_deadline:
                    raise ValidationError(
                        _("The task's end date (%s) cannot exceed the milestone's deadline (%s).")
                        % (record.end_date, milestone_deadline)
                    )

    @api.onchange('start_date', 'end_date', 'milestone_id')
    def _onchange_task_dates(self):
        if self.milestone_id:
            milestone_start = self.milestone_id.start_date
            milestone_deadline = self.milestone_id.deadline

            # Check if start_date is before the milestone's start_date
            if milestone_start and self.start_date and self.start_date < milestone_start:
                return {
                    'warning': {
                        'title': _("Invalid Start Date"),
                        'message': _("The start date cannot be before the milestone's start date (%s).")
                                   % milestone_start,
                    }
                }

            # Check if end_date is after the milestone's deadline
            if milestone_deadline and self.end_date and self.end_date > milestone_deadline:
                return {
                    'warning': {
                        'title': _("Invalid End Date"),
                        'message': _("The end date cannot exceed the milestone's deadline (%s).")
                                   % milestone_deadline,
                    }
                }

    @api.depends('start_date', 'end_date')
    def _compute_task_duration(self):
        for record in self:
            if record.start_date and record.end_date:
                duration = (record.end_date - record.start_date).days
                record.task_duration = max(duration, 0)
            else:
                record.task_duration = 0

    @api.depends('end_date')
    def _compute_remaining_days(self):
        for record in self:
            if record.end_date:
                days_left = (record.end_date - fields.Date.today()).days
                record.remaining_days = max(days_left, 0)
            else:
                record.remaining_days = 0

    @api.depends('remaining_days')
    def _compute_warning(self):
        for record in self:
            if record.remaining_days == 0:
                record.warning = 'late'
            elif record.remaining_days <= 2:  # Customize threshold for approaching deadline
                record.warning = 'approaching_deadline'
            else:
                record.warning = 'on_plan'

    def action_task_start(self):
        for record in self:
            if record.project_id.state == "draft":
                raise ValidationError("Cannot start task while the project is in 'Draft' state.")
            if record.project_id.state == "complete":
                raise ValidationError("Cannot start task for a completed project.")
            if not record.start_date:
                raise ValidationError("Start date must be set before starting the task.")
            if record.state == 'draft':
                record.state = "in_progress"
                record.progress = 0.0
                record.milestone_id.state = 'in_progress'
            else:
                raise ValidationError("Task can only be started from the 'Draft' state.")

    def action_task_complete(self):
        for record in self:
            if record.state == 'in_progress':
                record.state = "complete"
                if all(task.state == 'complete' for task in record.milestone_id.task_ids):
                    record.milestone_id.state = 'complete'


    @api.model
    def create(self, vals):
        task = super(OsoulTask, self).create(vals)
        # If a task is created under a milestone that already has tasks in progress, ensure the milestone state is correct
        milestone = task.milestone_id
        if milestone and any(task.state != 'draft' for task in milestone.task_ids):
            milestone.state = 'in_progress'
        return task

    def write(self, vals):
        result = super(OsoulTask, self).write(vals)
        # Re-check milestone state after updating tasks
        for task in self:
            milestone = task.milestone_id
            if milestone:
                if all(task.state == 'complete' for task in milestone.task_ids):
                    milestone.state = 'complete'
                elif any(task.state != 'draft' for task in milestone.task_ids):
                    milestone.state = 'in_progress'
                else:
                    milestone.state = 'draft'
        return result
