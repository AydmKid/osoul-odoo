from odoo import _, api, fields, models, tools

class OsoulVehicleBrand(models.Model):
    _name = 'osoul.vehicle.brand'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _rec_name = 'name'
    
    name = fields.Char(string='brand', translate=True, required=True, tracking=True)
    model_ids = fields.One2many(comodel_name="osoul.vehicle.model", inverse_name="brand_id", tracking=True)



class OsoulVehicleModel(models.Model):
    _name = 'osoul.vehicle.model'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin'] 
    _rec_name = 'name'

    name = fields.Char(string='Model Name', translate=True, required=True, tracking=True)
    brand_id = fields.Many2one('osoul.vehicle.brand', string='brand', required=True, tracking=True, ondelete='restrict')