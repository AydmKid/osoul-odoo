from odoo import models, fields

class OsoulHumanResources(models.Model):
    _inherit = 'hr.department'

    management_name_id = fields.Many2one(string='Management Name', comodel_name='osoul.hr.managements', ondelete='restrict')