from odoo import models, fields

class OsoulHumanResourcesUnit(models.Model):
    _name = 'osoul.hr.unit'
    _description ="Unit"
    _rec_name ="unit_name"

    unit_name = fields.Char(string='Unit Name')
    department_name_id = fields.Many2one(string='Department Name', comodel_name='hr.department', ondelete='restrict')