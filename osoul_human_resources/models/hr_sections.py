from odoo import _, api, fields, models, tools

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class OsoulHumanResourcesSection(models.Model):
    _inherit = 'hr.employee'

    section_name = fields.Char(string="Section")