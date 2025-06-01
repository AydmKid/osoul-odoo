from odoo import _, api, fields, models, tools

class SecuritySupplyType(models.Model):
    _name ="osoul.security.supply.types"
    _description = ""
    _rec_name = "supply_type"

    supply_type = fields.Char(string='Supply Type')
    color = fields.Integer(string="Color")