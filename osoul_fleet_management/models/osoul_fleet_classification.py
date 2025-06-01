from odoo import _, api, fields, models, tools

class OsoulFleetClassification(models.Model):
    _name = 'osoul.fleet.classification'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Classification", tracking=True, translate=True)