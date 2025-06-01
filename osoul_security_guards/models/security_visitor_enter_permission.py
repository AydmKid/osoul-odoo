from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
import random

class SecurityVisitorEnterPermission(models.Model):
    _name = "osoul.security.visitor.enter.permission"
    _description = ""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "permission_code"

    permission_code = fields.Char(string="Permission Code", readonly=True, tracking=True)
    # PERMIT INFORMATION
    permit_issuer_id = fields.Many2one('res.users', string="Permit Issuer", default=lambda self: self.env.user.id, readonly=True, tracking=True)
    related_employee_id = fields.Many2one('hr.employee', compute="_compute_related_employee", string='', tracking=True)
    employment_no_id = fields.Char(related='related_employee_id.employment_no', string="Employment No", tracking=True)
    department_id = fields.Many2one(related='related_employee_id.department_id', string="Department", tracking=True)
    # VISITOR INFORMATION
    visitor_name = fields.Many2one(comodel_name='res.partner', string='Visitor Name',
                                  domain = ['|',('in_out_state', '=', 'draft'), ('in_out_state', '=', 'outside_osoul')], ondelete='restrict', tracking=True)
    identity_no = fields.Char(related='visitor_name.identity_no', string="Identity No", readonly=True, tracking=True)
    mobile = fields.Char(related='visitor_name.mobile', string="Mobile", tracking=True)
    visit_type_id = fields.Many2one('osoul.security.visits.types', string='Visit Type')
    # VEHICLE INFORMATION
    vehicle_available = fields.Boolean(string="Vehicle Availability", tracking=True)
    plate_no = fields.Char(string="Plate No", size=7, tracking=True)
    plate_letters = fields.Char(string="Plate Letters", size=5, tracking=True,)
    note = fields.Text(string="Extra Informations", tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('expired', 'Expired'),], string='Status', default='draft', tracking=True)
    enter_exit_permission = fields.Selection([('draft', 'Draft'),
                                              ('allowed_enter', 'Allowed Enter'),
                                              ('exit_not_allowed', 'Exit Not Allowed'),
                                              ('allowed_exit', 'Allowed Exit'),
                                              ('visitor_out', 'Visitor Out')], default="draft", string="Enter Exit Allowed Visitor", tracking=True)
    gate_entry_record = fields.Char(string="Gate Entry Record", readonly=True, tracking=True)
    progress = fields.Integer(string="Progress", compute="_compute_progress")

    in_out_state= fields.Selection(
        related="visitor_name.in_out_state",
        string="Status",
        readonly=True,
        tracking=True,
    )
    # progress bar
    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == "draft":
                progress = random.randrange(10, 25)
            elif rec.state == "running":
                progress = random.randrange(50 , 75)
            elif rec.state == "expired":
                progress = 100
            else :
                progress = 0 
            rec.progress = progress


    # undelete
    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise ValidationError(_("You cannot delete a record that is not in 'Draft' state."))
            else:
                return super(SecurityVisitorEnterPermission, self).unlink()
    # plate latters
    @api.onchange('plate_letters')
    def _onchange_plate_letters(self):
        for record in self:
            if record.plate_letters:
                record.plate_letters = '-'.join([letter for letter in record.plate_letters])
    # plate number
    @api.onchange('plate_no')
    def _onchange_plate_no(self):
        for record in self:
            if record.plate_no:
                record.plate_no = '-'.join([letter for letter in record.plate_no])

    # AUTO RECORD CODING SYSTEM
    @api.model
    def create(self, vals):
        if vals.get('permission_code', 'New') == 'New':
            vals['permission_code'] = self.env['ir.sequence'].next_by_code('visitor_enter_permission_sequence') or 'New'
        return super(SecurityVisitorEnterPermission, self).create(vals)

    # USER_ID AND EMPLOYEE RELATION
    @api.depends('permit_issuer_id')
    def _compute_related_employee(self):
        for permission in self:
            if permission.permit_issuer_id:
                employee = self.env['hr.employee'].search([('user_id', '=', permission.permit_issuer_id.id)], limit=1)
                permission.related_employee_id = employee.id
            else:
                permission.related_employee_id = False

    # RUNNING BUTTON
    def action_running_permission(self):
        self.env['osoul.security.visitor.enter'].create({
             'visitor_name': self.visitor_name.id
        })
        self.state = "running"
        self.enter_exit_permission = "allowed_enter"
        self.gate_entry_record = self.env["ir.sequence"].next_by_code(
            "security_visits_types_sequence"
            )
        self.visitor_name.in_out_state ="inside_osoul"

    # GOING OUT PERMISSION
    def action_allowed_exit(self):
        self.enter_exit_permission = "allowed_exit"