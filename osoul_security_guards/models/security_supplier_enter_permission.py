from re import T
from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import random

class SecuritySupplierEnterPermission(models.Model):
    _name = "osoul.security.supplier.enter.permission"
    _description = ""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "permission_code"

    permission_code = fields.Char(string="Permission Code", readonly=True, tracking=True)
    # PERMIT ISSUER INFORMATIONS
    permit_issuer_id = fields.Many2one('res.users', string="Permit Issuer", default=lambda self: self.env.user.id, readonly=True, tracking=True)
    related_employee_id = fields.Many2one('hr.employee', compute="_compute_related_employee", string='', tracking=True)
    employment_no_id = fields.Char(related='related_employee_id.employment_no', string="Employment No", tracking=True)
    department_id = fields.Many2one(related='related_employee_id.department_id', string="Department", tracking=True)
    # SUPPLIER INFORMATIONS
    supplier_name = fields.Many2one(comodel_name='res.partner', string='Supplier Name',
                                    domain = ['|',('in_out_state', '=', 'draft'), ('in_out_state', '=', 'outside_osoul')],
                                    ondelete='restrict', tracking=True)
    identity_no = fields.Char(related='supplier_name.identity_no', string="Identity No", readonly=True, tracking=True)
    mobile = fields.Char(related='supplier_name.mobile', string="Mobile", tracking=True)
    # SUPPLYING TYPE
    supply_type_id = fields.Many2one('osoul.security.supply.types',string='Supply Type', ondelete='restrict', tracking=True)
    operation_type = fields.Selection([('delivery', 'Delivery'),
                                       ('loading', 'Loading'),
                                       ('both', 'Both')], string="Operation Type", tracking=True)
    # VEHICLE INFORMATIONS
    vehicle_available = fields.Boolean(string="Vehicle Availability", tracking=True, default=True)
    plate_no = fields.Char(string="Plate No", size=7, tracking=True)
    plate_letters = fields.Char(string="Plate Letters", size=5, tracking=True)
    note = fields.Text(string="Extra Informations", tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('running', 'Running'),
                              ('expired', 'Expired'),], string='Status', default='draft', tracking=True)
    enter_exit_permission = fields.Selection([('draft','Draft'),
                                              ('allowed_enter', 'Allowed Enter'),
                                              ('exit_not_allowed', 'Exit Not Allowed'),
                                              ('allowed_exit', 'Allowed Exit'),
                                              ('supplier_out','Supplier Out')], default="draft", string="Enter Exit Allowed", tracking=True)
    gate_entry_record = fields.Char(string="Gate Entry Record", readonly=True, tracking=True)
    progress = fields.Integer(string="Progress", compute="_compute_progress")
    
    in_out_state= fields.Selection(
        related="supplier_name.in_out_state",
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
                progress = random.randrange(50, 80)
            elif rec.state == "expired":
                progress = 100
            else :
                progress = 0 
            rec.progress = progress

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
            vals['permission_code'] = self.env['ir.sequence'].next_by_code('supllier_entry_permission_sequence') or 'New'
        return super(SecuritySupplierEnterPermission, self).create(vals)

    # USER_ID AND EMPLOYEE RELATION
    @api.depends('permit_issuer_id')
    def _compute_related_employee(self):
        for permission in self:
            if permission.permit_issuer_id:
                employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
                permission.related_employee_id = employee.id
            else:
                permission.related_employee_id = False


    # RUNNING BUTTON
    def action_running_permission(self):
        self.env['osoul.security.supplier.enter'].create({
            'supplier_name': self.supplier_name.id
        })
        self.state = "running"
        self.enter_exit_permission = "allowed_enter"
        self.gate_entry_record = "permission_code_id"
        self.supplier_name.in_out_state ="inside_osoul"

        
    # GOING OUT PERMISSION
    def action_allowed_exit(self):
        self.enter_exit_permission = "allowed_exit"
    
    def unlink(self):
        for permission in self:
            if permission.state in ['running', 'expired']:
                raise UserError(_("You cannot delete a permission record in 'running' or 'expired' state."))
            supplier_enter = self.env['osoul.security.supplier.enter'].search([('permission_code_id', '=', permission.id)])
            if supplier_enter:
                supplier_enter.unlink()
        return super(SecuritySupplierEnterPermission, self).unlink()