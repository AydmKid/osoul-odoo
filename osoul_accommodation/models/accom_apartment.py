from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class AccomApartment(models.Model):
    _name = "osoul.accommodation.apartment"
    _description = "Accommodation Apartment"
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name ="apartment_no"


    apartment_no  = fields.Char(String="Apartment No", required=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", ondelete='restrict', tracking=True)
    housing = fields.Selection(related='employee_id.host_accom',string="Housing Status", tracking=True)
    building_id = fields.Many2one(comodel_name='osoul.accommodation.building', required=True ,string="Building", ondelete='restrict', tracking=True)
    building_name = fields.Char(related='building_id.building_name', string="Building Name", tracking=True)
    total_apartment = fields.Integer(related='building_id.total_apartments',string="Total Apartment",tracking=True)
    room_id = fields.Many2one(comodel_name='osoul.accommodation.room', string="Total room", ondelete='restrict', tracking=True)
    rooms_no = fields.Char(string="Room No", tracking=True)
    total_rooms = fields.Integer(string="Total Rooms",compute="_compute_total_room",tracking=True)
    # floor_id  = fields.Many2one(comodel_name='osoul.accommodation.floor',string='')
    floors_id = fields.Many2one(comodel_name='osoul.accommodation.floor',domain="[('id', 'in', floor_ids)]",string='', required=True) 
    floor_no = fields.Selection(related='floors_id.floor_no',domain="[('building_id', '=', active_id)]",String="Floor No")
    floor_ids = fields.Many2many(comodel_name='osoul.accommodation.floor',)
    housing_status = fields.Selection(
        related="employee_id.host_accom",
        string="Hosing Status",
        readonly=True,
        tracking=True,
    )

    log_line_ids = fields.One2many('osoul.accommodation.log.line.stock.apartment', 'logs_ids', string="Stock Items Used")

    @api.model
    def create(self, vals):
        return super(AccomApartment, self).create(vals)

    def write(self, vals):
        return super(AccomApartment, self).write(vals)



    @api.constrains('apartment_no')
    def _check_unique_apartment_no(self):
        for record in self:
            if record.apartment_no:
                duplicate_apartments = self.search([('id', '!=', record.id), ('apartment_no', '=', record.apartment_no),('building_id','=', self.building_id.id)])
                if duplicate_apartments:
                    raise ValidationError(_("Apartment No must be unique."))

    @api.onchange('building_id')
    def onchange_building(self):
        self.floor_ids =  self.env['osoul.accommodation.floor'].search([('building_id', '=', self.building_id.id)]).ids

    def _compute_total_room(self):
        for record in self:
            rooms = self.env['osoul.accommodation.room'].search([('apartment_id', '=', record.id)])
            record.total_rooms = len(rooms)
    
    

    def action_open_rooms(self):
        return{
            'type':'ir.actions.act_window',
            'name':_("Rooms"),
            'res_model':'osoul.accommodation.room',
            'view_mode':'tree,form',
            'target':'current',
            'context':{'default_apartment_id':self.id,'create': False},
            'domain': [('apartment_id', '=', self.id)]
        }