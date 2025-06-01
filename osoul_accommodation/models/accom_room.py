import logging
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import date

# Set up logger
_logger = logging.getLogger(__name__)

class AccomRoom(models.Model):
    _name = "osoul.accommodation.room"
    _description = ""
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name = "room_no"

    room_no = fields.Char(string="Room No", copy=False)
    user_id = fields.Many2one(stirng="Username", comodel_name='res.users', default=lambda self: self.env.user, readonly=True)
    building_id = fields.Many2one(comodel_name='osoul.accommodation.building', string="Building", ondelete='restrict', tracking=True)
    building_name = fields.Char(related='building_id.building_name', string="Building Name", tracking=True ,store=True)
    building_location = fields.Selection(related='building_id.location', string="Building Location", tracking=True,store=True)
    floor = fields.Selection([('first_floor', 'First Floor'),
                              ('second_floor', 'Second Floor'),
                              ('third_floor', 'Third Floor'),
                              ('forth_floor', 'Forth Floor')], string="Floor No", tracking=True)
    total_beds = fields.Integer(string="Total Beds", tracking=True)
    empty_beds = fields.Integer(string="Empty Beds", compute="_compute_empty_beds", store=True, tracking=True)
    total_residents = fields.Integer(string="Total Residents", compute="_compute_total_residents", tracking=True)
    # country_id = fields.Many2one(related='employee_id.country_id',string='Nationality')
    housing_percentage = fields.Integer(string="Housing Perecentage", compute="_compute_housing_percentage", tracking=True)
    housing_relation_ids = fields.One2many(comodel_name="osoul.accommodation.housing", inverse_name="room_relation_id", ondelete='restrict', tracking=True)
    housing_status = fields.Selection([('ready','Ready'),('not_ready','Not Ready')], default="not_ready")
    state = fields.Selection([('unhoused','Unhoused'),
                              ('space_available', 'Space Available'),
                              ('room_is_full', 'Room Is Full'),
                              ('extra', 'Extra')
                              ], string='Status', default='unhoused', tracking=True)
    floor_id  = fields.Many2one(comodel_name='osoul.accommodation.floor',string='Floor No')
    apartment_id = fields.Many2one(comodel_name='osoul.accommodation.apartment',string='Apartment NO')
    floor_ids = fields.Many2many(comodel_name='osoul.accommodation.floor',)
    apartment_ids = fields.Many2many(comodel_name='osoul.accommodation.apartment',compute='_compute_apartment_ids')
    # max_capacity = fields.Integer(string='Max Capacity',compute="_compute_housing_capacity")
    image = fields.Binary("Building Image", attachment=True)
    standard_bed = fields.Integer(string="Standard Beds", default=2, tracking=True)

    
    log_line_ids = fields.One2many('osoul.accommodation.log.line.stock.room', 'logs_ids', string="Stock Items Used")

    @api.model
    def create(self, vals):
        return super(AccomRoom, self).create(vals)

    def write(self, vals):
        return super(AccomRoom, self).write(vals)

        
    
    time_spent_inside = fields.Integer(
        string="Time Spent Inside",
        store=True,
    )



    @api.depends('total_beds', 'total_residents')
    def _compute_empty_beds(self):
        for record in self:
            empty_beds = record.total_beds - record.total_residents
            record.empty_beds = empty_beds if empty_beds >= 0 else 0
    
    
    _sql_constraints = [
        ('unique_room_no', '', '')
    ]



    @api.onchange('building_id')
    def onchange_building(self):
        self.floor_id = False
        self.floor_ids =  self.env['osoul.accommodation.floor'].search([('building_id', '=', self.building_id.id)]).ids
        # self.apartment_ids =  False
        # if self.floor_id and self.building_id:
            # self.apartment_ids = self.env['osoul.accommodation.apartment'].search([('floors_id', '=', self.floor_id.id),('building_id', '=', self.building_id.id)]).ids

    # @api.onchange('floor_id')
    # def onchange_floor(self):
    #     # self.floor_ids =  self.env['osoul.accommodation.floor'].search([('building_id', '=', self.building_id.id)]).ids
    #     self.apartment_id =  False
    #     if self.floor_id and self.building_id:
    #         self.apartment_ids = self.env['osoul.accommodation.apartment'].search([('floors_id', '=', self.floor_id.id),('building_id', '=', self.building_id.id)]).ids

    @api.depends('floor_id')
    def _compute_apartment_ids(self):
        for record in self:
            if record.floor_id and record.building_id:
                apartments = self.env['osoul.accommodation.apartment'].search([
                    ('floors_id', '=', record.floor_id.id),
                    ('building_id', '=', record.building_id.id)
                ])
                record.apartment_ids = [(6, 0, apartments.ids)]
            else:
                record.apartment_ids = [(5, 0, 0)]



    # room_num = fields.Integer(string='Room Number')
    

    # UNIQUE ROOM NO
    # _sql_constraints = [
    #     ('unique_room_no', 'unique(room_no)', 'Room No must be unique.'),]

    # START HOUSING BUTTON
    def action_button_housing_ready(self):
        for record in self:
            if record.total_beds <= 0 :
                raise ValidationError(_("Can not start housing without beds availabilty, add beds before"))
            else:
                record.housing_status = "ready"

    def action_button_housing_not_ready(self):
        for record in self:
            if record.total_residents != 0:
                raise ValidationError(_("There is residents still inside room, you need to remove them before stop housing in this room"))
            else:
                record.housing_status = "not_ready"

    # COMPUTE TOTAL RESIDENTS
    @api.depends('housing_relation_ids')
    def _compute_total_residents(self):
        for record in self:
            record.total_residents = len(record.housing_relation_ids)

    

    # @api.depends('total_residents')
    # def _compute_housing_capacity(self):
    #     for record in self:
    #         if record.total_beds and record.total_residents:
    #             if record.total_beds > 0:
    #                 record.max_capacity = (record.total_residents / record.total_beds) * 100 - 10
    #         else:
    #             record.max_capacity = 0

    # PERCENTAGE CALCULATIONS
    @api.depends('total_residents', 'standard_bed', 'total_beds')
    def _compute_housing_percentage(self):
        for record in self:
            if record.standard_bed and record.total_residents:
                if record.standard_bed > 0:
                    if record.state == 'extra' and record.total_residents > record.standard_bed:
                        record.housing_percentage = (record.total_residents / record.standard_bed) * 100 
                    else:
                        record.housing_percentage = (record.total_residents / record.total_beds) * 100
                else:
                    record.housing_percentage = 0
            else:
                record.housing_percentage = 0

    
    # STATE CONTROL
    @api.onchange('total_residents', 'standard_bed')
    def onchange_field(self):
        for record in self:
            if record.total_residents == 0:
                record.state = "unhoused"
            elif record.total_residents > 0 and record.total_residents < record.total_beds:
                record.state = "space_available"
            elif record.total_residents == record.total_beds and record.total_beds == record.standard_bed or record.total_residents == record.total_beds and record.standard_bed > record.total_beds:
                record.state = "room_is_full"
            elif record.total_beds > record.standard_bed and record.total_residents > record.standard_bed:
                record.state = "extra"
                if record.total_residents > record.total_beds:
                    raise ValidationError(_("Room cannot hold new members, add more beds to add a new member"))
            else:
                raise ValidationError(_("Room cannot hold new members, add more beds to add a new member"))

    
    
    def open_bed_wizard(self):
        self.ensure_one()
        return {
            'name': _('Modify Beds'),
            'type': 'ir.actions.act_window',
            'res_model': 'osoul.accommodation.beds.control.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': {'default_room_id': self.id},
        }