from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class AccomFloor(models.Model):
    _name = "osoul.accommodation.floor"
    _description = "Accommodation Floor"
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name ="floor_name_id"


    floor_no  = fields.Selection([('first', 'The First'),
                              ('second', 'The Second'),
                              ('third', 'The Third'),
                              ('fourth', 'The Fourth')],string="Floor No")
    building_id = fields.Many2one(comodel_name='osoul.accommodation.building',required=True, string="Building", ondelete='restrict', tracking=True)
    building_name = fields.Char(related='building_id.building_name', string="Building Name", tracking=True)
    total_floors = fields.Integer(related='building_id.total_floors',string="Total Flooor",tracking=True)
    room_id = fields.Many2one(comodel_name='osoul.accommodation.room', string="Total room", ondelete='restrict', tracking=True)
    rooms_no = fields.Char(string="Room No", tracking=True)
    total_apartment = fields.Integer(string="Total Apartment",compute="_compute_total_room",tracking=True)
    floor_name_id = fields.Many2one(comodel_name='osoul.accommodation.floor.name', string='Floor Name',required=True)

    log_line_ids = fields.One2many('osoul.accommodation.log.line.stock.floor', 'logs_ids', string="Stock Items Used")

    @api.model
    def create(self, vals):
        return super(AccomFloor, self).create(vals)

    def write(self, vals):
        return super(AccomFloor, self).write(vals)

    @api.constrains('floor_name_id', 'building_id')
    def _check_unique_floor_no(self):
        for record in self:
            if record.floor_name_id and record.building_id:
                duplicate_floors = self.search([
                    ('id', '!=', record.id),
                    ('floor_name_id', '=', record.floor_name_id.id),
                    ('building_id', '=', record.building_id.id)
                ])
                if duplicate_floors:
                    raise ValidationError(_("The floor already exists on this building !"))

    @api.onchange('building_id')
    def _onchange_building_id(self):
        if self.building_id:
            self.floor_no = False
            self.total_floors = self.building_id.total_floors
        else:
            self.floor_no = False
            self.total_floors = False

    @api.constrains('total_floors')
    def _check_total_floors(self):
        for record in self:
            if record.total_floors > 4:
                raise ValidationError("Total Floors cannot exceed 4.")

    def _compute_total_room(self):
        for record in self:
            apartmet = self.env['osoul.accommodation.apartment'].search([('floors_id', '=', record.id)])
            record.total_apartment = len(apartmet)
    
    

    def action_open_apartment(self):
        return{
            'type':'ir.actions.act_window',
            'name':_("apartment"),
            'res_model':'osoul.accommodation.apartment',
            'view_mode':'tree,form',
            'target':'current',
            'context':{'default_floors_id':self.id,'create': False,},
            'domain': [('floors_id', '=', self.id)]
        }


class AccomFloorName(models.Model):
    _name = "osoul.accommodation.floor.name"
    _description = "Accommodation Floor Name"
    _rec_name =""

    name  = fields.Char(string="Name")
