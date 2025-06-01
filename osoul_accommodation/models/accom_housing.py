from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import date
from datetime import datetime

class AccomHousing(models.Model):
    _name = "osoul.accommodation.housing"
    _description = ""
    _inherit = 'mail.thread','mail.activity.mixin'
    _rec_name = "employee_id"

    building_id = fields.Many2one(related='room_relation_id.building_id', string="Building Id", ondelete='restrict', tracking=True)
    building_name = fields.Char(related='room_relation_id.building_name', string="Building Name", tracking=True)
    building_location = fields.Selection(related='room_relation_id.building_location', string="Building Location",tracking=True)
    room_relation_id = fields.Many2one(comodel_name="osoul.accommodation.room", ondelete='restrict', tracking=True)
    room_no = fields.Char(related='room_relation_id.room_no', string="Room No", tracking=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", ondelete='restrict', tracking=True) 
    employement_no = fields.Char(related='employee_id.employment_no', string="Employment No", tracking=True)
    department = fields.Many2one(related='employee_id.department_id', string="Department", readonly=True, tracking=True,store=True)
    job_id = fields.Many2one(related='employee_id.job_id', string="Job ID", tracking=True)
    mobile_phone = fields.Char(related='employee_id.work_phone', tracking=True)
    housing = fields.Selection(related='employee_id.host_accom',string="Housing Status", tracking=True)
    country_id = fields.Many2one(related='employee_id.country_id',string='Nationality')
    job_title = fields.Char(related='employee_id.job_title',string='Job Title',readonly=True ,tracking=True)
    management_name = fields.Many2one(related='employee_id.management_name',string='Management Name')
    # log_line_ids = fields.One2many(related='employee_id.log_line_ids', string="Stock Items Used")
    housing_exit_date = fields.Date(string='Expire Date', readonly=True, tracking=True)
    floor_id = fields.Many2one(related='room_relation_id.floor_id', string="Floor NO", tracking=True)
    apartment_id = fields.Many2one(related='room_relation_id.apartment_id', string="Apartment NO", tracking=True)
    housing_status = fields.Selection(
        related="employee_id.host_accom",
        string="Hosing Status",
        readonly=True,
        tracking=True,
    )

    current_date = fields.Datetime(string="Current Date", compute='_compute_housing_today')
    housing_date = fields.Datetime(string='Housing Date', store=True, default=fields.Datetime.now ,readonly=True)
    time_spent_inside = fields.Char(
        string="Time Spent Inside",
        
        store=True,
    )
    
    # Create current date
    @api.depends('create_date')
    def _compute_housing_today(self):
        for record in self:
            record.current_date = fields.Datetime.now()

    
    @api.model
    def create(self, vals):
        housing_records = super(AccomHousing, self).create(vals)
        if housing_records.employee_id:
            housing_records.employee_id.host_accom = "hosted"
            # housing_records._compute_time_spent_inside()  # Compute time_spent_inside
            accommodation_log = self.env['osoul.accommodation.log']
            accommodation_log.create({
                'employee_id': housing_records.employee_id.id,
                'room_relation_id': housing_records.room_relation_id.id,
                'building_id': housing_records.building_id.id,
                'floor_id': housing_records.floor_id.id,
                'housing_date': housing_records.housing_date
                
            })
        return housing_records

    def unlink(self):
        exit_date = fields.date.today()
        accommodation_log = self.env['osoul.accommodation.log']
        for rec in self:
            rec
            if rec.employee_id and rec.room_relation_id:
                rec.employee_id.host_accom = "not_hosted"
                rec.room_relation_id.state = "space_available"
                rec.housing_exit_date = exit_date
                log_records = accommodation_log.search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('room_relation_id', '=', rec.room_relation_id.id)
                ])
                log_records.write({
                    'housing_exit_date': exit_date,
                })
            rec.room_relation_id.total_residents -= 1
            if rec.room_relation_id.total_residents == 0:
                rec.room_relation_id.state = "unhoused"
            else:
                rec.room_relation_id.state = "space_available"
            rec.housing_exit_date = exit_date
        return super(AccomHousing, self).unlink()

    def action_button_delete(self):
        for record in self:
            record.unlink()