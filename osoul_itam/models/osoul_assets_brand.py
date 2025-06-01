from odoo import _, api, fields, models, tools

class OsoulItamAssetsBrand(models.Model):
    _name = 'osoul.itam.assets.brand'
    _description = 'brands for ITAM System'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    _sql_constraints = [
        ('unique_brand_name', 'unique(name)', 
         'The brand name must be unique. Please choose a different name.')]

    name = fields.Char(string='brand Name', required=True, tracking=True, help="Name of the brand.")
