from odoo import _, api, fields, models, tools

class OsoulWaterCounters(models.Model):
    _name = "osoul.water.counter"
    _description = ""
    _rec_name = "trip_no"

    trip_no = fields.Char(string='Reference', required=True, copy=False, readonly=True, store=True)
    vehicle_id = fields.Many2one('osoul.water.tanker', string='Vehicle', readonly=True, store=True, ondelete='restrict')
    owner_id = fields.Many2one(comodel_name="osoul.water.vendor", string="Vendor", readonly=True, store=True, ondelete='restrict')
    driver_id = fields.Many2one('osoul.tanker.driver', string='Driver Name', readonly=True, store=True, ondelete='restrict')
    water_type = fields.Selection(
        [('high_salinity', 'High Salinity'), ('low_salinity', 'Low salinity'),
         ('residential_desalination_water', 'Residential desalination water'),
         ('commercial_desalinated_water', 'Commercial desalinated water'),
         ('desalinated_water_with_tax', 'Desalinated water with tax')], tracking=True, readonly=True)
    filling_date = fields.Datetime(string="Filling Date", readonly=True, store=True)
    filling_station = fields.Selection([('a', 'A Station'), ('b', 'B Station'), ('c', 'C Station'),
                                ('d', 'D Station'), ('e', 'E Station'), ('f', 'F Station'), ('g', 'G Station')], tracking=True, readonly=True, store=True)
    curr_read_cone = fields.Float(string="CRead C.One", tracking=True, readonly=True, store=True)
    curr_read_ctwo = fields.Float(string="CRead C.Two", tracking=True, readonly=True, store=True)
    curr_read_cthree = fields.Float(string="CRead C.Three", tracking=True, readonly=True, store=True)
    filled_water_cone = fields.Float(string="Filled WC.One", store=True)
    filled_water_ctwo = fields.Float(string="Filled WC.Two", store=True)
    filled_water_cthree = fields.Float(string="Filled WC.Three", store=True)
    total_filled_water = fields.Float(string="T.Filled Water", store=True)
    total_cost = fields.Float(string="Cost", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id,
                                  required=True, readonly=True)