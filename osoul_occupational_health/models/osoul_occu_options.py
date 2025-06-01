from odoo import _, api, fields, models, tools

class OsoulOccuWorkType(models.Model):
    _name = 'osoul.occu.work.type'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Work Type")





class OsoulOccuHazard(models.Model):
    _name = 'osoul.occu.hazard'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Hazard")





class OsoulOccuMeasures(models.Model):
    _name = 'osoul.occu.actions'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Taken Action")





class OsoulOccuPersonalProtective(models.Model):
    _name = 'osoul.occu.personal.protective'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="PPE")