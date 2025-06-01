from odoo import _, api, fields, models, tools

class AccomBuilding(models.Model):
    _name = "osoul.accommodation.building"
    _description = ""
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name = "building_name"

    building_no = fields.Char(string="Building No", tracking=True)
    building_name = fields.Char(string="Building Name", translate=True, tracking=True)
    location = fields.Selection([('osoul_poultry', 'Osoul Poultry'),
                                 ('operation_office', 'Operation Office'),
                                 ('osoul_hatchery', 'Osoul Hatchery'),
                                 ('osoul_jeddah', 'Osoul Jeddah'),
                                 ('osoul_jizan', 'Osoul Jizan'),
                                 ('osoul_abha', 'Osoul Abha')], string="Building Location", tracking=True)
    total_rooms = fields.Integer(string="Total Rooms", compute="_compute_total_rooms", tracking=True)
    totals_rooms = fields.Integer(string="Total Rooms", tracking=True)
    total_beds = fields.Integer(string="Total Beds", compute="_compute_total_beds", tracking=True)
    totals_beds = fields.Integer(string="Total Beds", tracking=True)
    standard_bed = fields.Integer(string="Standard Bed", compute="_compute_standard_bed", tracking=True)
    standards_beds = fields.Integer(string="Standards Beds", tracking=True)

    total_residents = fields.Integer(string="Total Residents", compute="_compute_total_residents", tracking=True)
    totals_residents = fields.Integer(string="Total Residents", tracking=True)
    total_floors = fields.Integer(string="Total Floor",compute="_compute_total_floor" , tracking=True)
    totals_floors = fields.Integer(string="Total Floors", tracking=True)
    total_apartments = fields.Integer(string='Total Apartment',compute="_compute_total_apartment")
    totals_apartments = fields.Integer(string="Total Apartments", tracking=True)
    total_wc = fields.Integer(string="Total WC", tracking=True)
    total_entries = fields.Integer(string="Total Entries", tracking=True)
    total_emergency_exits = fields.Integer(string="Total Emergency Exits", tracking=True)
    housing_percentage = fields.Integer(string="Housing Perecentage", compute="_compute_housing_percentage", default=0, tracking=True)
    max_energy = fields.Integer(string='Total Energy',compute="_compute_housing_max_capacity")
    state = fields.Selection([('building_not_full', 'Building Not Full'),
                              ('building_is_full', 'Building Is Full'),], string='Status',
                             compute="_compute_housing_status",default='building_not_full',tracking=True)
    building_floor_id = fields.Many2one(comodel_name='osoul.accommodation.floor', string="Floor", ondelete='restrict', tracking=True)
    total_all_residents = fields.Integer(string="Total All Residents", compute="_compute_total_all_residents", store=True)

    @api.depends('total_residents', 'totals_residents','location')
    def _compute_total_all_residents(self):
        for record in self:
            location = record.location
            all_buildings = self.env['osoul.accommodation.building'].search([('location', '=', location)])
            total_all_residents = sum(building.total_residents for building in all_buildings)
            record.total_all_residents = total_all_residents

    is_unique_per_location = fields.Boolean(string="Unique Per Location", compute='_compute_is_unique_per_location')

    @api.depends('location')
    def _compute_is_unique_per_location(self):
        location_seen = set()
        for record in self:
            if record.location not in location_seen:
                record.is_unique_per_location = True
                location_seen.add(record.location)
            else:
                record.is_unique_per_location = False


    

    @api.constrains('total_floors')
    def _check_total_floors(self):
        for record in self:
            if record.total_floors > 4:
                raise ValidationError("Total Floors cannot exceed 4.")


    @api.depends('total_residents', 'total_beds')
    def _compute_housing_percentage(self):
        for record in self:
            if record.total_beds != 0:
                record.housing_percentage = (record.total_residents / record.total_beds) * 100
            else:
                record.housing_percentage = 0

    @api.depends('total_residents', 'total_beds')
    def _compute_housing_max_capacity(self):
        for record in self:
            if record.total_beds != 0:
                record.max_energy = (record.total_residents / record.total_beds) * 100 - 10
            else:
                record.max_energy = 0


    @api.depends('housing_percentage')
    def _compute_housing_status(self):
        for record in self:
            if record.housing_percentage >= 100:
                record.state = "building_is_full"
            else:
                record.state = "building_not_full"

    def _compute_total_residents(self):
        for record in self:
            residents = self.env['osoul.accommodation.room'].search([('building_id', '=', record.id)])
            total_residents = sum(room.total_residents for room in residents)
            record.total_residents = total_residents
            record.totals_residents = record.total_residents

    _sql_constraints = [
    ('unique_building_name_location', 'UNIQUE(building_name, location)', 'Building name must be unique within the location.'),
    ('unique_building_name', 'CHECK (NOT (building_name IS NULL AND location IS NULL))', 'Building name cannot be null for a specific location.')
        ]

    def _compute_total_rooms(self):
        for record in self:
            rooms = self.env['osoul.accommodation.room'].search_count([('building_id','=',record.id)])
            record.total_rooms = rooms
            record.totals_rooms = record.total_rooms

    def _compute_total_floor(self):
        for record in self:
            floor = self.env['osoul.accommodation.floor'].search([('building_id', '=', record.id)])
            record.total_floors = len(floor)
            record.totals_floors = record.total_floors

    
    def _compute_total_apartment(self):
        for record in self:
            apartment = self.env['osoul.accommodation.apartment'].search([('building_id', '=', record.id)])
            record.total_apartments = len(apartment)
            record.totals_apartments = record.total_apartments

    def _compute_total_beds(self):
        for record in self:
            beds = self.env['osoul.accommodation.room'].search([('building_id', '=', record.id)])
            total_beds = sum(room.total_beds for room in beds)
            record.total_beds = total_beds
            record.totals_beds = record.total_beds

    def _compute_standard_bed(self):
        for record in self:
            beds = self.env['osoul.accommodation.room'].search([('building_id', '=', record.id)])
            standard_bed = sum(room.standard_bed for room in beds)
            record.standard_bed = standard_bed
            record.standards_beds = record.standard_bed



    def action_open_floors(self):
        return{
            'type':'ir.actions.act_window',
            'name':_("Floors"),
            'res_model':'osoul.accommodation.floor',
            'view_mode':'tree,form',
            'target':'current',
            'context':{'default_building_id':self.id},
            'domain':[('building_id', '=', self.id)]
        }

    def action_open_rooms(self):
        return{
            'type':'ir.actions.act_window',
            'name':_("Rooms"),
            'res_model':'osoul.accommodation.room',
            'view_mode':'tree,form',
            'target':'current',
            'context':{'default_building_id':self.id},
            'domain': [('building_id', '=', self.id)]
        }

    def action_open_apartment(self):
        return{
            'type':'ir.actions.act_window',
            'name':_("apartment"),
            'res_model':'osoul.accommodation.apartment',
            'view_mode':'tree,form',
            'target':'current',
            'context':{'default_building_id':self.id},
            'domain': [('building_id', '=', self.id)]
        }