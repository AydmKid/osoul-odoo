from odoo import _, api, fields, models, tools

class OsoulFleetWorkRole(models.Model):
    _name = 'osoul.fleet.work.role'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Work Role", tracking=True, translate=True)