from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    token = fields.Char(string='Token', help='Unique token for the user')

    