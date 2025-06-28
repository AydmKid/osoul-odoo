from odoo import models, fields, api, _

class OsoulOccuTaskAssignment(models.Model):
    _name = 'osoul.occu.task.assignment'
    _description = 'Task Assignment for Team Members'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'task_name'
    _order = 'create_date desc'

    task_name = fields.Char(string="Task Title", required=True, tracking=True)
    description = fields.Text(string="Task Description")
    assigned_to = fields.Many2one('osoul.occu.team', string="Assigned To", required=True, tracking=True)
    due_date = fields.Date(string="Due Date", tracking=True)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ], string="Priority", default='medium', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('task_created', 'Task Created'),
        ('in_progress', 'In Progress'),
        ('done', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', tracking=True)

    def action_create(self):
        for rec in self:
            rec.state = 'task_created'

    def action_start(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
