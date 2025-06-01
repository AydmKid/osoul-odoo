from odoo import _, api, fields, models, tools

class OsoulFleetOwner(models.Model):
    _name ='osoul.fleet.owner'
    _description =''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Owner", tracking=True, translate=True)