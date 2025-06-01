from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import date

class AccommodationLog(models.Model):
    _name = 'osoul.accommodation.log'
    _description = 'Accommodation Log'
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name = 'employee_id'


    building_id = fields.Many2one(comodel_name='osoul.accommodation.building', string="Building", ondelete='restrict', tracking=True)
    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="Employee Name",domain=[('host_accom', '=', 'not_hosted')], 
                                  ondelete='restrict', tracking=True)
    room_relation_id = fields.Many2one(comodel_name="osoul.accommodation.room", ondelete='restrict', tracking=True)
    employement_no = fields.Char(related='employee_id.employment_no', string="Employment No", tracking=True)
    department = fields.Many2one(related='employee_id.department_id', string="Department", tracking=True,store=True)
    housing = fields.Selection(related='employee_id.host_accom',string="Housing Status", tracking=True)
    country_id = fields.Many2one(related='employee_id.country_id',string='Nationality',readonly=True ,tracking=True)
    job_title = fields.Char(related='employee_id.job_title',string='Job Title',readonly=True ,tracking=True)


    building_name = fields.Char(related='building_id.building_name', string="Building Name", tracking=True)
    floor_id  = fields.Many2one(comodel_name='osoul.accommodation.floor',string='Floor No')
    apartment_id = fields.Many2one(related='room_relation_id.apartment_id', string="Apartment NO", tracking=True)
    room_no = fields.Char(related='room_relation_id.room_no', string="Room No", tracking=True)
    building_location = fields.Selection(related='room_relation_id.building_location', string="Building Location", tracking=True)
    floor_ids = fields.Many2many(comodel_name='osoul.accommodation.floor')

    stock_id = fields.Many2many(comodel_name='osoul.accommodation.stock', string="Stock Items")
    product_name = fields.Char(related='stock_id.product_name',string="Product Name", tracking=True)

    housing_date = fields.Date(string='Housing Date', store=True, tracking=True)
    housing_exit_date = fields.Date(string='Exit Date', readonly=True, tracking=True)
    current_date = fields.Datetime(string="Current Date",default=fields.Datetime.now())

    log_line_ids = fields.One2many('osoul.accommodation.log.line.stock.emp', 'log_id', string="Stock Items Used")


    @api.model
    def create(self, vals):
        return super(AccommodationLog, self).create(vals)

    def write(self, vals):
        return super(AccommodationLog, self).write(vals)


    
    time_spent_inside = fields.Integer(
        string="Time Spent Inside",
        store=True,
    )

    # Compute time spent inside
    @api.onchange('housing_date', 'current_date')
    def _onchange_housing_date(self):
        if self.housing_date and self.current_date:
            housing_date = fields.Datetime.from_string(self.housing_date)
            current_date = fields.Datetime.from_string(self.current_date)
            delta = current_date - housing_date
            self.time_spent_inside = delta.days
        else:
            self.time_spent_inside = 0

    def compute_time_spent_button(self):
        self._compute_time_spent_inside()
        return True

    counts_atten = fields.Integer(compute="_compute_count")

    def _compute_count(self):
        self.counts_atten = 0
        for rec in self:
           attends = rec.search([('employee_id','=',rec.employee_id.id)])
           rec.counts_atten = len(attends)


    def open_emp_record(self):
        context = {
            'employee_id': self.employee_id.id,
            'create': False 
        }
        employee_name = self.employee_id.name if self.employee_id else ""
        return {
            'type': 'ir.actions.act_window',
            'name': employee_name,
            'view_mode': 'list',
            'view_type': 'form',
            'res_model': 'osoul.accommodation.log',
            'target': 'new',
            'context': context,
            'domain': [('employee_id', '=', self.employee_id.id)]
        }

    def open_emp_profile(self):
        
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.employement_no}",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'hr.employee',
            'target': 'self',
            'context': {'force_detailed_view': 'true'},
            'domain' : [('id','=',self.employee_id.id)],
            'res_id': self.employee_id.id,
        }


    #Find the current floor
    @api.onchange('building_id')
    def onchange_building(self):
        self.floor_id = False
        self.floor_ids =  self.env['osoul.accommodation.floor'].search([('building_id', '=', self.building_id.id)]).ids
    
    
    #State control
    housing_status = fields.Selection(
        related="employee_id.host_accom",
        string="Hosing Status",
        readonly=True,
        tracking=True,
    )

class CustomDepartment(models.Model):
    _name = 'custom.department'
    _description = 'Custom Department'

    name = fields.Char(string="Department Name", required=True)