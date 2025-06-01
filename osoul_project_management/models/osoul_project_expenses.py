from odoo import _, api, fields, models, tools

class OsoulExpense(models.Model):
    _name = 'osoul.project.expense'
    _description = 'Osoul Expense'

    name = fields.Char(string="Expense Name", required=True)
    description = fields.Text(string="Description")
    date = fields.Date(string="Expense Date", default=fields.Date.today)
    amount = fields.Float(string="Amount", required=True)
    category = fields.Selection([
        ('item', 'Item'),
        ('service', 'Service'),
        ('other', 'Other')
    ], string="Category", required=True, default='other')
    project_id = fields.Many2one('osoul.project', string="Project", ondelete='cascade', readonly=True)