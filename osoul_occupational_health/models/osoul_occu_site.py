from odoo import _, api, fields, models, tools

class OsoulOccuSite(models.Model):
    _name = 'osoul.occu.site'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Site", required=True, tracking=True)
    location_ids = fields.One2many('osoul.occu.location', 'site_id')



class OsoulOccuLocation(models.Model):
    _name = 'osoul.occu.location'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Location", required=True, tracking=True)
    site_id = fields.Many2one(comodel_name='osoul.occu.site', ondelete='cascade')