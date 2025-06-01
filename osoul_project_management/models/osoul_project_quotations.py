from odoo import models, fields

class OsoulQuotation(models.Model):
    _name = 'osoul.quotation'
    _description = 'Osoul Quotation'

    name = fields.Char(string="Quotation Name", required=True)
    vendor = fields.Many2one(comodel_name="res.partner", tracking=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Date", default=fields.Date.today)
    amount = fields.Float(string="Amount", tracking=True)
    recommendations = fields.Text(string="Recommendations", tracking=True)
    state = fields.Selection([("draft", "Draft"), ('rejected', 'Rejected'), ('accepted', 'Accepted')], default="draft", readonly=True, tracking=True)
    project_id = fields.Many2one('osoul.project', string="Project", ondelete='cascade', readonly=True)
    document = fields.Binary(string="Upload Quotation Document")
    document_name = fields.Char(string="Document Name")

    def _update_milestone_state(self):
        for milestone in self:
            task_states = milestone.task_ids.mapped('state')
            if not task_states or all(state == 'draft' for state in task_states):
                milestone.state = 'draft'
            elif all(state == 'complete' for state in task_states):
                milestone.state = 'complete'
            else:
                milestone.state = 'in_progress'

    def action_rejected(self):
        self.state = 'rejected'

    def action_accepted(self):
        self.state = 'accepted'