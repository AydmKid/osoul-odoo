from odoo import _, api, fields, models, tools
from odoo.tools.translate import _


class SecurityPoultryGates(models.Model):
    _name = "osoul.security.poultry.gates"
    _description = "Security Poultry Gates"
    _rec_name = "gate_name"

    gate_no = fields.Char(
        string="Gate No", help="Gate number for identification")
    gate_name = fields.Char(
        string="Gate Name", help="Name of the poultry gate", translate=True
    )
    gate_location = fields.Selection(
        [
            ("east_side", "East Side"),
            ("west_side", "West Side"),
            ("north_side", "North Side"),
            ("south_side", "South Side"),
        ],
        string="Gate Location",
        help="Location of the poultry gate",
    )
