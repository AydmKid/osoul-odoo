from odoo import _, api, fields, models, tools

class ResUsrsInfo(models.Model):
    _inherit = 'res.users'

    token = fields.Char(string='Token', help='Unique token for the user')
    responsible_unit = fields.Selection([
        ('networks', 'Networks'),
        ('systems', 'Systems'),
        ('technical_support', 'Technical Support'),
        ('developers', 'Developers'),
        ('operation', 'Operation'),
        ('information_technology_office', 'Information Technology Office')
    ], string='unit')
    

    

    