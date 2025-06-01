from odoo import _, api, fields, models, tools

class ResUsersInfo(models.Model):
    _inherit = 'res.users'

    tokeen = fields.Char(string='Token', help='Unique token for the user')
    responsible_unit = fields.Selection([
        ('networks', 'Networks'),
        ('systems', 'Systems'),
        ('technical_support', 'Technical Support'),
        ('developers', 'Developers'),
        ('operation', 'Operation'),
        ('information_technology_office', 'Information Technology Office')
    ], string='unit')
    

    

    