from odoo import _, api, fields, models, tools

class OsoulFleetCategory(models.Model):
    _name = 'osoul.fleet.category'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Category", tracking=True, translate=True)