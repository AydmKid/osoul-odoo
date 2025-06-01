from odoo import fields, models

class TransportationVehicle(models.Model):
    _name = 'transportation.vehicle'
    _description = 'Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Vehicle Name", required=True)
    license_plate = fields.Char(string="License Plate", required=True)
    driver_id = fields.Many2one('osoul.transportation.driver', string="Assigned Driver")
    vehicle_type = fields.Selection([
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('bus', 'Bus'),
        ('motorbike', 'Motorbike')
    ], string="Vehicle Type", required=True)
    active = fields.Boolean(string="Active", default=True)
    vehicle_image = fields.Binary(string="Vehicle Image", attachment=True)
