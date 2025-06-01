from odoo import _, api, fields, models, tools

class OsoulAssetsLocations(models.Model):
    _name = "osoul.assets.locations"

    name = fields.Char(string="Location")