from odoo import models, fields

class FirebaseToken(models.Model):
    _name = 'firebase.token'
    _description = 'Firebase Device Tokens'

    token = fields.Char(string='Device Token', required=True, unique=True)
    user_id = fields.Many2one('res.users', string='User', help='User associated with this token')
