from odoo import _, api, fields, models, tools

class OsoulFleetPlateTypes(models.Model):
    _name = 'osoul.fleet.plate.type'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Plate Type", tracking=True, translate=True)