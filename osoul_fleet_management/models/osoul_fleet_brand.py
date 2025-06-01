from odoo import _, api, fields, models, tools
from odoo.addons.bus.models.bus import dispatch

class OsoulFleetBrand(models.Model):
    _name = 'osoul.fleet.brand'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Brand", tracking=True, translate=True)