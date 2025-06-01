from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
import re
import logging

#==================================================================================================================================
# VENDOR INFORMATION
#==================================================================================================================================

class OsoulWaterVendor(models.Model):
    _name = "osoul.water.vendor"
    _description = "Water vendor"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    sequence = fields.Char(string="Vendor No")
    name = fields.Char(string="Vendor Name", translate=True, required=True, tracking=True)
    phone = fields.Char(string="Phone No", default="+966", required=True, tracking=True)
    total_drivers = fields.Integer(string="Total Drivers", compute="_compute_total_drivers", store=True, readonly=True)
    total_vehicles = fields.Integer(string="Total Vehicles", compute="_compute_total_vehicles", store=True, readonly=True)
    driver_ids = fields.One2many(comodel_name="osoul.tanker.driver", inverse_name="vendor_id", tracking=True, ondelete="restrict")
    vehicle_ids = fields.One2many(comodel_name="osoul.water.tanker", inverse_name="owner_id", tracking=True, ondelete="restrict")
    capacity = fields.Float(string="Capacity", compute="_compute_vendor_capacity", store=True)
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('suspended', 'Suspended')], default="draft", tracking=True)
    contracts = fields.Integer(string="Contracts", compute="_compute_total_contracts", store=True)
    trips = fields.Integer(string="Trips", compute="_compute_trips", store=True)
    delivered_water = fields.Float(string="Delivered Water", compute="_compute_delivered_water", store=True)
    counter_ids = fields.One2many(comodel_name="osoul.water.counter", inverse_name="owner_id", string="Water Counters")
    contract_ids = fields.One2many(comodel_name="osoul.water.contract", inverse_name="second_party", string="Contracts")

    _sql_constraints = [
        ('vendor_phone_unique', 'UNIQUE(phone)', 'The phone number must be unique')]

    # MODEL CREATE
    # VENDOR SEQUENCE NUMBER
    @api.model
    def create(self, vals):
        if not vals.get('sequence'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.water.vendor') or '/'
        return super(OsoulWaterVendor, self).create(vals)

    # DEPENDS AND COMPUTES
    # CALCULATE MAXIMUM CAPACITY FOR VENDOR TANKER TRUCKS
    @api.depends('vehicle_ids.capacity')
    def _compute_vendor_capacity(self):
        for record in self:
            record.capacity = sum(record.vehicle_ids.mapped('capacity')) if record.vehicle_ids else 0
    
    # COMPUTE TOTAL DRIVER WITH VENDOR
    @api.depends('driver_ids')
    def _compute_total_drivers(self):
        for vendor in self:
            vendor.total_drivers = len(vendor.driver_ids)

    # COMPUTE TOTAL TANKER TRUCKS WITH VENDOR
    @api.depends('vehicle_ids')
    def _compute_total_vehicles(self):
        for vendor in self:
            vendor.total_vehicles = len(vendor.vehicle_ids)

    # COMPUTE TOTAL CONTRACTS
    @api.depends('contract_ids.second_party')  # Correct dependency
    def _compute_total_contracts(self):
        for record in self:
            record.contracts = self.env['osoul.water.contract'].search_count([('second_party', '=', record.id)])

    # COMPUTE TOTAL TRIPS
    @api.depends('counter_ids')  # Ensure 'counter_ids' exists as a One2many
    def _compute_trips(self):
        for record in self:
            record.trips = len(record.counter_ids)

    # COMPUTE DELIVERED WATER
    @api.depends('counter_ids.total_filled_water')  # Improved dependency
    def _compute_delivered_water(self):
        for record in self:
            record.delivered_water = sum(record.counter_ids.mapped("total_filled_water"))


    # BUTTONS
    def action_active(self):
        for record in self:
            record.state = "active"

    def action_suspended(self):
        for record in self:
            record.state = "suspended"

    def show_contract(self):
        return{
            'name': 'Contracts',
            'res_model': 'osoul.water.contract',
            'view_mode': 'list,form',
            'context':{},
            'target': 'current',
            'type': 'ir.actions.act_window'}
    
    def show_total_rtips(self):
        return{
            'name': 'Trips',
            'res_model': 'osoul.water.counter',
            'view_mode': 'list,form',
            'context':{},
            'target': 'current',
            'type': 'ir.actions.act_window'}
    
    def show_total_loads(self):
        return{
            'name': 'Water Delivered',
            'res_model': 'osoul.water.counter',
            'view_mode': 'list,form',
            'context':{},
            'target': 'current',
            'type': 'ir.actions.act_window'}

#==================================================================================================================================
# DRIVER INFORMATION
#==================================================================================================================================

class OsoulTankerDriver(models.Model):
    _name = 'osoul.tanker.driver'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
     
    vendor_no = fields.Char(string="Vendor No", related="vendor_id.sequence", readonly=True)
    name = fields.Char(string='Driver Name', translate=True, required=True, tracking=True)
    nationlaity_id = fields.Many2one('res.country', string='Nationality', required=True, tracking=True, ondelete='restrict')
    phone = fields.Char(string='Phone No', default="+966", required=True, tracking=True)
    vendor_id = fields.Many2one(comodel_name="osoul.water.vendor",tracking=True, ondelete='restrict')
    status = fields.Selection(
        [('draft', 'Draft'),  ('inside_osoul', 'Inside Osoul'), ('outside_osoul', 'Outside Osoul')],
        default='outside_osoul', readonly=True)
    
    _sql_constraints = [
        ('driver_phone_unique', 'UNIQUE(phone)', 'The phone number must be unique')]


#==================================================================================================================================
# VEHICLE INFORMATION
#==================================================================================================================================

_logger = logging.getLogger(__name__)
class OsoulWaterTankerInformation(models.Model):
    _name = 'osoul.water.tanker'
    _description = 'Water Tanker Information'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    # Basic Information Fields
    vendor_no = fields.Char(string="Vendor No", related="owner_id.sequence", readonly=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    brand_id = fields.Many2one('osoul.vehicle.brand', string='brand', required=True, tracking=True, ondelete='restrict')
    model_id = fields.Many2one('osoul.vehicle.model', string='Vehicle Model', required=True, domain="[('brand_id', '=', brand_id)]",
                                tracking=True, ondelete='restrict')
    plate_letters = fields.Char(string='Plate Letters', required=True, size=3, tracking=True)
    plate_no = fields.Char(string='Plate Numbers', required=True, size=4, tracking=True)
    full_plate = fields.Char(string='Plate No', compute='_compute_full_plate', store=True)
    capacity = fields.Float(string='Capacity', required=True, tracking=True)
    owner_id = fields.Many2one('osoul.water.vendor', string='Owner Name', required=True, tracking=True, ondelete='restrict')
    owner_phone = fields.Char(related='owner_id.phone', string='Owner Phone No', readonly=True)
    status = fields.Selection(
        [('draft', 'Draft'), ('inside_osoul', 'Inside Osoul'), ('outside_osoul', 'Outside Osoul')],
        default='outside_osoul',
        readonly=True,
        tracking=True)
    vehicle_reception_count = fields.Integer(string='Water Reception Count', compute='_compute_vehicle_reception_count', store=False)

    # SQL Constraints
    _sql_constraints = [
        ('unique_full_plate', 'unique(full_plate)', 'The Plate Number must be unique.')
    ]

    @api.depends('model_id', 'full_plate')
    def _compute_display_name(self):
        for record in self:
            model_name = record.model_id.name if record.model_id else ''
            full_plate = record.full_plate or ''
            record.display_name = f"{model_name} [{full_plate}]"
            
    @api.depends('plate_letters', 'plate_no')
    def _compute_full_plate(self):
        for record in self:
            record.full_plate = f"{record.plate_letters or ''}-{record.plate_no or ''}"

    def _compute_vehicle_reception_count(self):
        for record in self:
            record.vehicle_reception_count = self.env['osoul.water.reception'].search_count([('vehicle_id', '=', record.id)])

    # Constraints
    @api.constrains('plate_letters')
    def _check_plate_letters(self):
        for record in self:
            if record.plate_letters and not re.match("^[A-Z]+$", record.plate_letters):
                raise ValidationError("Plate Letters must contain only uppercase alphabetic characters.")

    @api.constrains('capacity')
    def _check_capacity(self):
        for record in self:
            if record.capacity <= 0:
                raise ValidationError("Capacity must be a positive integer.")

    # Onchange Methods
    @api.onchange('plate_letters')
    def _onchange_plate_letters(self):
        if self.plate_letters:
            self.plate_letters = self.plate_letters.upper()

    @api.onchange('brand_id')
    def _onchange_name(self):
        """Clear the model name if the brand is changed."""
        if self.brand_id:
            self.model_id = False

    # Override create method to log creation
    @api.model
    def create(self, vals):
        record = super(OsoulWaterTankerInformation, self).create(vals)
        _logger.info(f"Water Tanker Information record created with ID: {record.id}")
        return record

    # Override write method to log updates
    def write(self, vals):
        res = super(OsoulWaterTankerInformation, self).write(vals)
        _logger.info(f"Water Tanker Information record updated with ID: {self.id}")
        return res

    # Action to view related water trips
    def action_view_water_trips(self):
        """Returns an action to display the related water reception records."""
        self.ensure_one()
        action = self.env.ref('osoul_water_management.osoul_water_reception_action').read()[0]
        action['domain'] = [('vehicle_id', '=', self.id)]
        action['context'] = dict(self.env.context, default_vehicle_id=self.id)
        return action
    



#==================================================================================================================================
# VEHICLE BARDS AND MODELS
#==================================================================================================================================

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