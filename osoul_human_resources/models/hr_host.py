from odoo import models, fields

class OsoulHumanResourcesHost(models.Model):
    _name = 'osoul.hr.host'
    _description =""
    _rec_name ="Hosting"


    host_name  = fields.Char(string="Host")