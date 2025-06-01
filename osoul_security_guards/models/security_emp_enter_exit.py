from odoo import _, api, fields, models, tools
from datetime import datetime
from datetime import date
from odoo.exceptions import UserError
import random


class SecurityEmployeeEntryExit(models.Model):
    _name = "osoul.security.emp.enter.exit"
    _description = "Security Employee Entry and Exit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "emp_name_id"


    @api.model
    def create(self, vals):
        if vals.get('exit_reason') == 'permission':
            vals['state'] = 'out_permission'
            vals['time_out'] = fields.Datetime.now()
        return super(SecurityEmployeeEntryExit, self).create(vals)

    def write(self, vals):
        if 'exit_reason' in vals and vals['exit_reason'] == 'permission':
            vals['state'] = 'out_permission'
            vals['time_out'] = fields.Datetime.now()
        return super(SecurityEmployeeEntryExit, self).write(vals)

    record_no = fields.Char(string="Record No", tracking=True)
    note = fields.Text(string="Note",tracking=True)
    emp_name_id = fields.Many2one(
        string="Employee Name",
        comodel_name="hr.employee",
        ondelete="restrict",
        required=True,
        domain=['|', ('in_out_status', '=', 'draft'), ('in_out_status', '=', 'outside_osoul'), ('host_accom', '=', 'not_hosted')],
        tracking=True,
    )

    # @api.onchange('emp_name_id')
    # def _onchange_emp_name_id(self):
    #     if self.emp_name_id:
    #         status = self.emp_name_id.in_out_status
    #         if status == 'inside_osoul':
    #             emp_name = self.emp_name_id.name or "Unknown Employee"
    #             self.emp_name_id = False
    #             return {
    #                 'warning': {
    #                     'title': "Warning!",
    #                     'message': _("The employee %s is currently Inside Osoul.") % emp_name,
    #                 }
    #             }
    
    emp_id_no = fields.Char(
        related="emp_name_id.employment_no", string="Employee ID", tracking=True,
        
    )
    country_id = fields.Many2one(related='emp_name_id.country_id',string='Nationality',readonly=True ,tracking=True)
    
    emp_housing = fields.Selection(
        related="emp_name_id.host_accom",
        string="Housing",
        readonly=True, 
        tracking=True,
    )

    emp_department_id = fields.Many2one(
        related="emp_name_id.department_id",
        string="Department",
        readonly=True,
        store=True,
        tracking=True,
    )

    work_location_id = fields.Many2one(
        related="emp_name_id.work_location_id",
        string="Work Location",
        readonly=True,
        store=True,
        tracking=True,
    )


    emp_phone = fields.Char(
        related="emp_name_id.mobile_phone", string="Phone No", tracking=True
    )
    in_out_status = fields.Selection(
        related="emp_name_id.in_out_status",
        string="Status",
        readonly=True,
        tracking=True,
    )
    time_in = fields.Datetime(string="Entering Time", readonly=True, tracking=True)
    entry_gate_id = fields.Many2one(
        string="Entering Gate",
        comodel_name="osoul.security.poultry.gates",
        ondelete="restrict",
        tracking=True,
        default=lambda self: self._default_entry_gate_id(),
    )
    guard_in_entry_id = fields.Many2one(
        string="Entering Guard",
        comodel_name="res.users",
        ondelete="restrict",
        tracking=True,
    )
    
    def _default_entry_gate_id(self):
        # You can define your logic here to determine the default value
        # For example, you can return the first gate in the gates model
        gates = self.env['osoul.security.poultry.gates'].search([], limit=1)
        return gates and gates.id or False

    time_out = fields.Datetime(string="Exiting Time", readonly=True, tracking=True)
    exit_gate_id = fields.Many2one(
        string="Exiting Gate",
        comodel_name="osoul.security.poultry.gates",
        ondelete="restrict",
        tracking=True,
        default=lambda self: self._default_entry_gate_id(),
    )
    guard_in_exiting_id = fields.Many2one(
        string="Exiting Guard",
        comodel_name="res.users",
        ondelete="restrict",
        tracking=True,
    )
    time_spent_inside = fields.Char(
        string="Time Spent Inside",
        compute="_compute_time_spent_inside",
        store=True,
        tracking=True,
    )

    Expiration_of_working_hours = fields.Selection(
        [
            ('complete', 'Complete Work day'),
            ('incomplete', 'Incomplete Work day'),
        ],
        string="Expiration of Working Hours",
        compute="_compute_Expiration_of_working_hours",
        store=True,
        tracking=True,
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("inside_osoul", "Inside Osoul"),
            ("out_permission", "Out Permission"),
            ("outside_osoul", "Outside Osoul"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )

    entry_reason = fields.Selection(
        [
         ('start_of_work', 'Start of work'),
         ('job_assignment', 'Job assignment'),
        ],
        string='Entery Reason',
        default='start_of_work',
        tracking=True,

    )

    exit_reason  = fields.Selection(
         [
            ('end_of_work', 'End of work'),
            ('permission', 'Permission'),
            ('job_assignment', 'Job assignment'),
         ],
         string="Exit Reason",
         default="end_of_work",
         tracking=True,
    )

    @api.onchange('exit_reason')
    def _onchange_exit_reason(self):
        if self.exit_reason == 'permission':
            self.state = 'out_permission'
            self.time_out = fields.Datetime.now()

    hours_on_permission = fields.Selection(
         [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
         ],
         string="Hours On Permission",
         tracking=True,
    )
    
    permission_time = fields.Datetime(string="Permission Time", compute='_compute_permission_time', store=True, readonly=True, tracking=True)
    

    @api.depends('hours_on_permission')
    def _compute_permission_time(self):
        for record in self:
            if record.hours_on_permission in ['1', '2', '3']:
                record.permission_time = fields.Datetime.now()
                record.guard_in_exiting_id = self.env.user.id
            else:
                record.permission_time = False


    back_permission = fields.Selection(
         [
            ("draft", "Draft"),
            ('he_is_back', 'He Is Back'),
            ('he_is_not_back', 'He Is Not Back'),
         ],
         string="Back Permission",
         default="draft",
         tracking=True,
         store=True,
    )

    @api.onchange('back_permission')    
    def _onchange_back_permission(self):
        if self.back_permission == 'he_is_back':
            self.state = 'inside_osoul'
        elif self.back_permission == 'he_is_not_back':
            self.state = 'outside_osoul'
            self.emp_name_id.in_out_status = "outside_osoul"

    
        

    back_permission_time = fields.Datetime(string="Back Permission Time", compute='_compute_back_permission_time', store=True, readonly=True, tracking=True)

    @api.depends('back_permission')
    def _compute_back_permission_time(self):
        for record in self:
            if record.back_permission == 'he_is_back':
                record.back_permission_time = fields.Datetime.now()
                record.guard_in_entry_id = self.env.user.id
            else:
                record.back_permission_time = False

    time_difference = fields.Float(string="Time Difference (Hours)", compute='_compute_time_difference', store=False)

    @api.depends('permission_time', 'back_permission_time')
    def _compute_time_difference(self):
        for record in self:
            if record.permission_time and record.back_permission_time:
                permission_dt = datetime.strptime(str(record.permission_time), '%Y-%m-%d %H:%M:%S')
                back_permission_dt = datetime.strptime(str(record.back_permission_time), '%Y-%m-%d %H:%M:%S')
                time_diff = (back_permission_dt - permission_dt).total_seconds() / 3600  # Convert seconds to hours
                record.time_difference = time_diff
            else:
                record.time_difference = 0.0  # Default to 0 if either field is missing

                

    event_date = fields.Date(default=date.today())

    progress = fields.Integer(string="Progress", compute="_compute_progress")

    
    counts_atten = fields.Integer(compute="_compute_count")

    def _compute_count(self):
        self.counts_atten = 0
        for rec in self:
           attends = rec.search([('emp_name_id','=',rec.emp_name_id.id)])
           rec.counts_atten = len(attends)


    def open_records(self):
        context = {
            'emp_name_id': self.emp_name_id.id,  # Assuming emp_name_id is a Many2one field
            'create': False 
                }
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.emp_id_no}",
            'view_mode': 'tree',
            'view_type': 'form',
            'res_model': 'osoul.security.emp.enter.exit',
            'target': 'dialog',
            'context': context,
            'domain' : [('emp_name_id','=',self.emp_name_id.id)]
        }

    def open_emp_record(self):
        
        return {
            'type': 'ir.actions.act_window',
            'name': f"{self.emp_id_no}",
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'hr.employee',
            'target': 'self',
            'context': {'force_detailed_view': 'true'},
            'domain' : [('id','=',self.emp_name_id.id)],
            'res_id': self.emp_name_id.id,
        }

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == "draft":
                progress = random.randrange(5, 25)
            elif rec.state == "inside_osoul":
                progress = random.randrange(50, 75)
            elif rec.state == "outside_osoul":
                progress = 100
            else:
                progress = 0
            rec.progress = progress

    @api.depends("time_spent_inside")
    def _compute_Expiration_of_working_hours(self):
        for record in self:
            time_spent_inside = record.time_spent_inside
            hours, minutes, seconds = map(int, time_spent_inside.split(':'))
            total_hours = hours + minutes / 60 + seconds / 3600

            if total_hours >= 8:
                record.Expiration_of_working_hours = 'complete'
            else:
                record.Expiration_of_working_hours = 'incomplete'

    @api.depends("time_in", "time_out")
    def _compute_time_spent_inside(self):
        for record in self:
            if record.time_in and record.time_out:
                time_in = record.time_in
                time_out = record.time_out
                time_spent = time_out - time_in
                hours = time_spent.seconds // 3600
                minutes = (time_spent.seconds // 60) % 60
                seconds = time_spent.seconds % 60
                record.time_spent_inside = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                record.time_spent_inside = "00:00:00"

    def action_button_inside_osoul(self):
        self.state = "inside_osoul"
        self.time_in = datetime.now()
        self.emp_name_id.in_out_status = "inside_osoul"
        self.guard_in_entry_id = self.env.user.id
        self.record_no = self.env["ir.sequence"].next_by_code(
            "security_emp_enter_exit_sequence"
        )

    def action_button_outside_osoul(self):
        self.state = "outside_osoul"
        self.time_out = datetime.now()
        self.emp_name_id.in_out_status = "outside_osoul"
        self.guard_in_exiting_id = self.env.user.id


    @api.model
    def _check_deletion_restrictions(self):
        restricted_states = ['inside_osoul']
        restrict_records = self.filtered(lambda r: r.state in restricted_states)
        if restrict_records:
            raise UserError(_("Deletion of records is not allowed when the state is 'inside_osoul' or 'outside_osoul'."))

    def unlink(self):
        self._check_deletion_restrictions()
        return super(SecurityEmployeeEntryExit, self).unlink()