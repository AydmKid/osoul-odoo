from odoo import _, api, fields, models, tools

class OsoulFleetOwner(models.Model):
    _name ='osoul.fleet.work.location'
    _description =''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Work Location", tracking=True, translate=True)