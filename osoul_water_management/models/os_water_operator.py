from odoo import _, api, fields, models, tools

class OsoulWaterOperator(models.Model):
    _name = 'osoul.water.operator'
    _description = 'Water Operator'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Many2one(comodel_name="hr.employee", string="Operator", tracking=True, ondelete="restrict")
    phone = fields.Char(string="Phone No", related='name.mobile_phone')