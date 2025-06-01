from odoo import _, api, fields, models, tools

class AccomKanDashBuilding(models.Model):
    _name = "osoul.accommodation.building.dash"
    _description = ""
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name = "location"

    building_no = fields.Char(string="Building No", tracking=True)
    image = fields.Binary("Location Image", attachment=True)
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
    standard_bed = fields.Integer(string="Standard Beds", default=2, compute="_compute_standard_beds",tracking=True)
    standards_beds = fields.Integer(string="Standard Beds", tracking=True)

    total_residents = fields.Integer(string="Total Residents", compute="_compute_total_residents", tracking=True)
    totals_residents = fields.Integer(string="Total Residents", tracking=True)
    total_floors = fields.Integer(string="Total Floor",compute="_compute_total_floor" , tracking=True)
    totals_floors = fields.Integer(string="Total Floors", tracking=True)
    total_apartments = fields.Integer(string='Total Apartment',compute="_compute_total_apartment")
    totals_apartments = fields.Integer(string="Total Apartments", tracking=True)
    total_wc = fields.Integer(string="Total WC", tracking=True)
    total_entries = fields.Integer(string="Total Entries", tracking=True)
    total_emergency_exits = fields.Integer(string="Total Emergency Exits", tracking=True)
    housing_percentage = fields.Float(string="Housing Perecentage", compute="_compute_housing_percentage", default=0, tracking=True)
    max_energy = fields.Integer(string='Total Energy',compute="_compute_housing_max_capacity")
    state = fields.Selection([('location_not_full', 'Location Not Full'),
                              ('location_is_full', 'Location Is Full'),], string='Status',
                             compute="_compute_housing_status",default='building_not_full',tracking=True)
    building_floor_id = fields.Many2one(comodel_name='osoul.accommodation.floor', string="Floor", ondelete='restrict', tracking=True)
    total_all_residents = fields.Integer(string="Total All Residents", compute="_compute_total_all_residents", store=True)
    total_beds_per_location = fields.Integer(string="Total Beds ", compute="_compute_total_beds_per_location")
    empty_beds_per_location = fields.Integer(string="Empty Beds", compute="_compute_empty_beds_per_location")
    standard_bed_per_location = fields.Integer(string="Standard Bed", compute="_compute_standard_bed_per_location")

    host_beds_per_location = fields.Integer(string="Hosted Beds", compute="_compute_host_beds_per_location")
    total_buildings_per_location = fields.Integer(string="Total Buildings ", compute="_compute_total_buildings_per_location",  store=True)
    promissory_note_copy = fields.Binary(string="Copy of Promissory Note",tracking=True)
    start_date_decade = fields.Date(string='Start Date', store=True, tracking=True)
    end_date_decade = fields.Date(string='End Date', store=True, tracking=True)
    total_rooms_per_location = fields.Integer(string="Total Rooms ", compute="_compute_total_rooms_per_location")
    empty_rooms_per_location = fields.Integer(string="Empty Rooms ", compute="_compute_empty_rooms_per_location")
    host_rooms_per_location = fields.Integer(string="Hosted Rooms", compute="_compute_host_rooms_per_location", store=True)
    is_tenant = fields.Boolean(string="Is Tenant")
    rent_value = fields.Integer(string="Rent value")
    difference_in_days = fields.Integer(string='Difference in Days', compute="_compute_difference_in_days", store=True ,readonly=True)
    city_name = fields.Char(string="City Name", translate=True, tracking=True)
    house_percentage = fields.Char(string="Housing Perecentage")

    

    def open_contract(self):
        self.ensure_one()
        
        # Determine if the create button should be enabled or not
        create_enabled = not self.env['osoul.accommodation.contrats.wizard'].search([
            ('state', '=', 'contract_running'),
            ('building_location', '=', self.location),
            ('building_id', '=', self.id)
        ], limit=1)

        return {
            'name': _("Contract"),
            'type': 'ir.actions.act_window',
            'res_model': 'osoul.accommodation.contrats.wizard',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'target': 'current',
            'domain': [('building_location', '=', self.location), ('building_id', '=', self.id)],
            'context': {
                'default_building_location': self.location,
                'default_building_id': self.id,
                'create': create_enabled,  # Control the visibility of the "Create" button
            },
            'flags': {'reload': True},  # Force the view to reload
        }


        

    @api.model
    def name_get(self):
        result = []
        for record in self:
            location_dict = dict(self.fields_get(allfields=['location'])['location']['selection'])
            location_name = location_dict.get(record.location, record.location)
            result.append((record.id, location_name))
        return result

    @api.onchange('is_tenant')
    def _onchange_is_tenant(self):
        if not self.is_tenant:
            self.start_date_decade = False
            self.end_date_decade = False
            self.difference_in_days = 0
            self.rent_value = 0.0
            self.promissory_note_copy = False

    @api.depends('start_date_decade', 'end_date_decade')
    def _compute_difference_in_days(self):
        for record in self:
            if record.start_date_decade and record.end_date_decade:
                start_date = fields.Date.from_string(record.start_date_decade)
                end_date = fields.Date.from_string(record.end_date_decade)
                record.difference_in_days = (end_date - start_date).days
            else:
                record.difference_in_days = 0

    @api.model
    def _cron_update_difference_in_days(self):
        records = self.search([])
        for record in records:
            record._compute_difference_in_days()


    @api.depends('location')
    def _compute_empty_rooms_per_location(self):
        for record in self:
            all_buildings = self.env['osoul.accommodation.building'].search([('location', '=', record.location)])
            empty_rooms_per_location = 0
            
            for building in all_buildings:
                rooms = self.env['osoul.accommodation.room'].search([('building_id', '=', building.id)])
                
                for room in rooms:
                    if not room.total_residents:
                        empty_rooms_per_location += 1
                        
            record.empty_rooms_per_location = empty_rooms_per_location


    @api.depends('location')
    def _compute_empty_beds_per_location(self):
        for record in self:
            buildings = self.env['osoul.accommodation.building'].search([('location', '=', record.location)])
            empty_beds_per_location = 0

            for building in buildings:
                rooms = self.env['osoul.accommodation.room'].search([('building_id', '=', building.id)])

                for room in rooms:
                    empty_beds = room.total_beds - room.total_residents  # Calculate empty beds in each room
                    empty_beds_per_location += empty_beds  # Add empty beds to the total

            record.empty_beds_per_location = empty_beds_per_location


    @api.depends('empty_beds_per_location', 'total_beds_per_location')
    def _compute_host_beds_per_location(self):
        for record in self:
            record.host_beds_per_location = record.total_beds_per_location - record.empty_beds_per_location
            

    @api.depends('location')
    def _compute_total_rooms_per_location(self):
        for record in self:
            location = record.location
            buildings = self.env['osoul.accommodation.room'].search_count([('building_location', '=', location)])
            record.total_rooms_per_location = buildings

    @api.depends('empty_rooms_per_location', 'total_rooms_per_location')
    def _compute_host_rooms_per_location(self):
        for record in self:
            record.host_rooms_per_location = record.total_rooms_per_location - record.empty_rooms_per_location
    

    @api.depends('location')
    def _compute_total_buildings_per_location(self):
        for record in self:
            location = record.location
            total_buildings_per_location = self.env['osoul.accommodation.building'].search_count([('location', '=', location)])
            record.total_buildings_per_location = total_buildings_per_location


    @api.depends('total_beds','totals_beds','location')
    def _compute_total_beds_per_location(self):
        for record in self:
            location = record.location
            all_building = self.env['osoul.accommodation.building'].search([('location', '=', location)])
            total_beds_per_location = sum(building.total_beds for building in all_building)
            record.total_beds_per_location = total_beds_per_location


    @api.depends('standard_bed','standards_beds','location')
    def _compute_standard_bed_per_location(self):
        for record in self:
            location = record.location
            all_building = self.env['osoul.accommodation.building'].search([('location', '=', location)])
            standard_bed_per_location = sum(building.standard_bed for building in all_building)
            record.standard_bed_per_location = standard_bed_per_location
    



    @api.depends('total_residents', 'totals_residents','location')
    def _compute_total_all_residents(self):
        for record in self:
            location = record.location
            all_buildings = self.env['osoul.accommodation.building'].search([('location', '=', location)])
            total_all_residents = sum(building.total_residents for building in all_buildings)
            record.total_all_residents = total_all_residents

    


    @api.constrains('total_floors')
    def _check_total_floors(self):
        for record in self:
            if record.total_floors > 4:
                raise ValidationError("Total Floors cannot exceed 4.")


    @api.depends('total_all_residents', 'standard_bed_per_location')
    def _compute_housing_percentage(self):
        for record in self:
            if record.standard_bed_per_location != 0:
                record.housing_percentage = (record.total_all_residents / record.standard_bed_per_location) * 100
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
                record.state = "location_is_full"
            else:
                record.state = "location_not_full"

    def _compute_total_residents(self):
        for record in self:
            residents = self.env['osoul.accommodation.room'].search([('building_id', '=', record.id)])
            total_residents = sum(room.total_residents for room in residents)
            record.total_residents = total_residents
            record.totals_residents = record.total_residents

    _sql_constraints = [
        ('unique_location', 'UNIQUE(location)', 'Location must be unique.')
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

    def _compute_standard_beds(self):
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