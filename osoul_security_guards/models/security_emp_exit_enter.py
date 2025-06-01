from odoo import _, api, fields, models, tools
from datetime import datetime
from odoo.exceptions import UserError
import random


class SecurityEmployeeExitEntry(models.Model):
    _name = "osoul.security.emp.exit.enter"
    _description = "Security Employee Exit and Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "emp_name_id"

    record_no = fields.Char(string="Record No", tracking=True)
    emp_name_id = fields.Many2one(
        string="Employee Name",
        comodel_name="hr.employee",
        ondelete="restrict",
        required=True,
        domain = ['|',('in_out_status', '=', 'draft'), ('in_out_status', '=', 'inside_osoul'),('host_accom', '=', 'hosted')],
        tracking=True,
    )
    # @api.onchange('emp_name_id')
    # def _onchange_emp_name_id(self):
    #     if self.emp_name_id:
    #         status = self.emp_name_id.in_out_status
    #         if status == 'outside_osoul':
    #             emp_name = self.emp_name_id.name
    #             self.emp_name_id = False
    #             return {
    #                 'warning': {
    #                     'title': "Warning!",
    #                     'message': _("The employee %s is currently Outside Osoul.") % emp_name,
    #                 }
    #             }
    emp_id_no = fields.Char(
        related="emp_name_id.employment_no", string="Employee ID", tracking=True

    )

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
    emp_phone = fields.Char(
        related="emp_name_id.mobile_phone", 
        string="Phone No", tracking=True
    )
    in_out_status = fields.Selection(
        related="emp_name_id.in_out_status",
        string="Status",
        readonly=True,
        tracking=True,
    )
    time_out = fields.Datetime(
        string="Exiting Time", readonly=True, tracking=True)
    exit_gate_id = fields.Many2one(
        string="Exiting Gate",
        comodel_name="osoul.security.poultry.gates",
        ondelete="restrict",
        tracking=True,
        default=lambda self: self.env['osoul.security.poultry.gates'].search([], limit=1),
    )
    guard_in_exiting_id = fields.Many2one(
        string="Exiting Guard",
        comodel_name="res.users",
        ondelete="restrict",
        tracking=True,
    )
    time_in = fields.Datetime(string="Entering Time",
                              readonly=True, tracking=True)
    entry_gate_id = fields.Many2one(
        string="Entering Gate",
        comodel_name="osoul.security.poultry.gates",
        ondelete="restrict",
        tracking=True,
        default=lambda self: self.env['osoul.security.poultry.gates'].search([], limit=1),
    )
    guard_in_entry_id = fields.Many2one(
        string="Entering Guard",
        comodel_name="res.users",
        ondelete="restrict",
        tracking=True,
    )
    time_spent_outsidee = fields.Char(
        string="Time Spent Outside",
        compute="_compute_time_spent_outside",
        store=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("outside_osoul", "Outside Osoul"),
            ("out_permission", "Out Permission"),
            ("inside_osoul", "Inside Osoul"),
        ],
        string="State",
        default="draft",
        tracking=True,
    )

   
    exit_type = fields.Selection(
        [
            ("normal_exit", "Normal Exit"),
            ('permission', 'Permission'),
            ("vacation", "Vacation"),
            ("final_exit", "Final Exit"),
        ],
        string="Exit Type",
        default="normal_exit",
        tracking=True,
    )

    

    hours_on_permission_exit = fields.Selection(
         [
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
         ],
         string="Hours On Permission",
         tracking=True,
         store=True,
    )

    permission_time_exit = fields.Datetime(string="Permission Time", compute='_compute_permission_time_exit', store=True, readonly=True, tracking=True)

    @api.depends('hours_on_permission_exit')
    def _compute_permission_time_exit(self):
        for record in self:
            if record.hours_on_permission_exit in ['1', '2', '3']:
                record.permission_time_exit = fields.Datetime.now()
                record.time_out = datetime.now()
                record.guard_in_exiting_id = self.env.user.id
            else:
                record.permission_time_exit = False

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

    


    back_permission_time_exit = fields.Datetime(string="Back Permission Time", compute='_compute_back_permission_time_exit', store=True, readonly=True, tracking=True)

    @api.depends('back_permission')
    def _compute_back_permission_time_exit(self):
        for record in self:
            if record.back_permission == 'he_is_back':
                record.back_permission_time_exit = fields.Datetime.now()
                record.time_in = datetime.now()
                record.guard_in_entry_id = self.env.user.id
            else:
                record.back_permission_time_exit = False

    time_difference = fields.Float(string="Time Difference (Hours)", compute='_compute_time_difference_exit', store=False)

    @api.depends('permission_time_exit', 'back_permission_time_exit')
    def _compute_time_difference_exit(self):
        for record in self:
            if record.permission_time_exit and record.back_permission_time_exit:
                permission_dt = datetime.strptime(str(record.permission_time_exit), '%Y-%m-%d %H:%M:%S')
                back_permission_dt = datetime.strptime(str(record.back_permission_time_exit), '%Y-%m-%d %H:%M:%S')
                time_diff = (back_permission_dt - permission_dt).total_seconds() / 3600  # Convert seconds to hours
                record.time_difference = time_diff
            else:
                record.time_difference = 0.0  # Default to 0 if either field is missing


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
            'res_model': 'osoul.security.emp.exit.enter',
            'target': 'fullscreen',
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
                progress = random.randrange(4, 25)
            elif rec.state == "outside_osoul":
                progress = random.randrange(50, 85)
            elif rec.state == "inside_osoul":
                progress = 100
            else :
                progress = 0 
            rec.progress = progress


    @api.depends("time_in", "time_out")
    def _compute_time_spent_outside(self):
        for record in self:
            if record.time_in and record.time_out:
                time_out = record.time_out
                time_in = record.time_in
                time_spent = time_in - time_out
                hours = time_spent.seconds // 3600
                minutes = (time_spent.seconds // 60) % 60
                seconds = time_spent.seconds % 60
                record.time_spent_outsidee = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                record.time_spent_outsidee = "00:00:00"

    from datetime import datetime

    def action_button_outside_osoul(self):
        for record in self:
            if record.exit_type == 'permission':
                record.state = 'out_permission'
            else:
                record.state = 'draft'
                record.state = "outside_osoul"
                record.time_out = datetime.now()
                record.emp_name_id.in_out_status = "outside_osoul"
                record.guard_in_exiting_id = self.env.user.id
                record.record_no = self.env["ir.sequence"].next_by_code("security_emp_exit_enter_sequence")

    def action_button_inside_osoul(self):
        self.state = "inside_osoul"
        self.time_in = datetime.now()
        self.emp_name_id.in_out_status = "inside_osoul"
        self.guard_in_entry_id = self.env.user.id

        

    @api.model
    def _check_deletion_restrictions(self):
        restricted_states = ['outside_osoul']
        restrict_records = self.filtered(
            lambda r: r.state in restricted_states)
        if restrict_records:
            raise UserError(
                _("Deletion of records is not allowed when the state is 'inside_osoul' or 'outside_osoul'."))

    def unlink(self):
        self._check_deletion_restrictions()
        return super(SecurityEmployeeExitEntry, self).unlink()