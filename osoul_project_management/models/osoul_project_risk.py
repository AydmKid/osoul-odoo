from odoo import _, api, fields, models, tools

class OsoulProjectRisk(models.Model):
    _name = 'osoul.project.risk'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Name", tracking=True)
    type = fields.Selection([('risk', 'Risk'), ('challenge', 'Challenge')], default="risk", tracking=True)
    description = fields.Text(string="Description", tracking=True)
    priority = fields.Selection([('low', 'Low'), ('middle', 'Middle'),
                                 ('high', 'Hight')], string="Priority", default="low", tracking=True)
    project_id = fields.Many2one(comodel_name='osoul.project', string="Project", ondelete='cascade')