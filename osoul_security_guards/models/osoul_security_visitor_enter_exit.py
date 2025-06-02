from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class SecurityVisitorEnterExit(models.Model):
    _name = "osoul.security.visitor.enter.exit"
    _description = "Security Visitor Entry and Exit"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "sequence"
    _order = 'create_date desc'
    
    sequence = fields.Char(string="Reference", required=True, readonly=True, copy=False, default='New')

    visitor_name = fields.Char(string="Visitor Name", required=True, tracking=True)
    visitor_id_no = fields.Char(string="ID No", required=True, tracking=True)
    visit_company = fields.Char(string="Company/Organization", tracking=True)
    visitor_mobile = fields.Char(string="Mobile", tracking=True)
    visitor_card_no = fields.Char(string="Card No", tracking=True)
    v_type_id = fields.Many2one('osoul.security.visits.types', string='Visit Type')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('inside', 'Inside Osoul'),
        ('exited', 'Exited'),
    ], string="State", default="draft", tracking=True)

    emp_name_id = fields.Many2one(
        string="Employee Name",
        comodel_name="hr.employee",
        ondelete="restrict",
        required=True,
        tracking=True,
    )
    emp_department_id = fields.Many2one(
        related="emp_name_id.department_id",
        string="Department",
        readonly=True,
        store=True,
        tracking=True,
    )

    time_in = fields.Datetime(string="Entry Time", tracking=True, readonly=True)
    time_out = fields.Datetime(string="Exit Time", tracking=True, readonly=True)

    time_spent_inside = fields.Char(
        string="Time Spent Inside",
        compute="_compute_time_spent_inside",
        store=True,
        tracking=True
    )

    day_name = fields.Char(string="Day Name", compute="_compute_day_name", store=True)
    stay_days = fields.Integer(string="Days No", tracking=True)

    entry_gate_id = fields.Many2one(
        comodel_name="osoul.security.poultry.gates",
        string="Entry Gate",
        required=True,
        default=lambda self: self._default_entry_gate_id(),
        tracking=True
    )
    exit_gate_id = fields.Many2one(
        comodel_name="osoul.security.poultry.gates",
        string="Exit Gate",
        required=True,
        default=lambda self: self._default_entry_gate_id(),
        tracking=True
    )
    guard_entry_id = fields.Many2one(
        comodel_name="res.users",
        string="Entry Guard",
        tracking=True
    )
    guard_exit_id = fields.Many2one(
        comodel_name="res.users",
        string="Exit Guard",
        tracking=True
    )

    note = fields.Text(string="Note", tracking=True)

    @api.depends('time_in')
    def _compute_day_name(self):
        day_translation = {
            'Monday': 'الاثنين',
            'Tuesday': 'الثلاثاء',
            'Wednesday': 'الأربعاء',
            'Thursday': 'الخميس',
            'Friday': 'الجمعة',
            'Saturday': 'السبت',
            'Sunday': 'الأحد',
        }
        for rec in self:
            if rec.time_in:
                english_day = rec.time_in.strftime('%A')
                rec.day_name = day_translation.get(english_day, english_day)
            else:
                rec.day_name = False

    @api.depends("time_in", "time_out")
    def _compute_time_spent_inside(self):
        for record in self:
            if record.time_in and record.time_out:
                delta = record.time_out - record.time_in
                hours = delta.seconds // 3600
                minutes = (delta.seconds // 60) % 60
                seconds = delta.seconds % 60
                record.time_spent_inside = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                record.time_spent_inside = "00:00:00"

    def _default_entry_gate_id(self):
        gates = self.env['osoul.security.poultry.gates'].search([], limit=1)
        return gates and gates.id or False

    def action_enter_osoul(self):
        self.state = 'inside'
        self.time_in = datetime.now()
        self.guard_entry_id = self.env.user.id

    def action_exit_osoul(self):
        self.state = 'exited'
        self.time_out = datetime.now()
        self.guard_exit_id = self.env.user.id

    def action_send_to_housing_manager(self):
        self.state = 'waiting_housing'

    @api.model
    def create(self, vals):
        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.security.visitor.enter.exit') or 'New'
        return super(SecurityVisitorEnterExit, self).create(vals)

    def unlink(self):
        if any(record.state == 'inside' for record in self):
            raise UserError(_("Cannot delete record while visitor is still inside."))
        return super(SecurityVisitorEnterExit, self).unlink()
    
    @api.constrains('visitor_id_no', 'visitor_mobile')
    def _check_unique_id_mobile(self):
        for rec in self:
            # Ensure ID number is exactly 10 digits and numeric
            if not rec.visitor_id_no.isdigit() or len(rec.visitor_id_no) != 10:
                raise ValidationError(_("ID No must be exactly 10 digits and numeric."))

            # Ensure mobile number is exactly 10 digits and numeric (if provided)
            if rec.visitor_mobile and (not rec.visitor_mobile.isdigit() or len(rec.visitor_mobile) != 10):
                raise ValidationError(_("Mobile number must be exactly 10 digits and numeric."))

            # Check for duplicate ID number where the state is 'inside'
            if self.search_count([
                ('visitor_id_no', '=', rec.visitor_id_no),
                ('id', '!=', rec.id),
                ('state', '=', 'inside')
            ]) > 0:
                raise ValidationError(_("A visitor with this ID No is already inside Osoul."))

            # Check for duplicate mobile number where the state is 'inside'
            if rec.visitor_mobile and self.search_count([
                ('visitor_mobile', '=', rec.visitor_mobile),
                ('id', '!=', rec.id),
                ('state', '=', 'inside')
            ]) > 0:
                raise ValidationError(_("A visitor with this mobile number is already inside Osoul."))

