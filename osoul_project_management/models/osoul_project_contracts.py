from odoo import models, fields

class OsoulContract(models.Model):
    _name = 'osoul.contract'
    _description = 'Osoul Contract'

    name = fields.Char(string="Contract Name", required=True)
    contractor_name = fields.Char(string="Contactor Name", tracking=True)
    contractor_type = fields.Selection([('person', 'Person'), ('compnay', 'Company')], string="Type", tracking=True)
    description = fields.Text(string="Description")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    amount = fields.Float(string="Amount")
    project_id = fields.Many2one('osoul.project', string="Project", ondelete='cascade')
    document = fields.Binary(string="Upload Contract Document")
    document_name = fields.Char(string="Document Name")