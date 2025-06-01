from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleExitPermit(models.Model):
    _name = 'osoul.transportation.exit.permit'
    _description = 'Vehicle Exit Permit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "permission_code"

    permission_code = fields.Char(string="Permission Code", readonly=True, tracking=True)
    # PERMIT ISSUER INFORMATIONS
    permit_issuer_id = fields.Many2one('res.users', string="Permit Issuer", default=lambda self: self.env.user.id, readonly=True, tracking=True)
    related_employee_id = fields.Many2one('hr.employee', compute="_compute_related_employee", string='', tracking=True)
    employment_no_id = fields.Char(related='related_employee_id.employment_no', string="Employment No", tracking=True)
    department_id = fields.Many2one(related='related_employee_id.department_id', string="Department", tracking=True)
    # Driver Info
    driver_id = fields.Many2one('osoul.transportation.driver', string="Assigned Driver")
    emp_id_no = fields.Char(related="driver_id.emp_id_no", string="Employee ID", tracking=True)
    emp_department_id = fields.Many2one(related="driver_id.emp_department_id",string="Department",readonly=True,store=True,tracking=True)
    country_id = fields.Many2one(related='driver_id.country_id',string='Nationality',readonly=True ,tracking=True)
    in_out_state= fields.Selection(
        related="driver_id.in_out_state",
        string="Status",
        readonly=True,
        tracking=True,
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('expired', 'Expired')
    ], string='Status', default='draft', tracking=True)
    enter_exit_permission = fields.Selection([('draft','Draft'),
                                              ('allowed_enter', 'Allowed Enter'),
                                              ('exit_not_allowed', 'Exit Not Allowed'),
                                              ('allowed_exit', 'Allowed Exit'),
                                              ('supplier_out','Supplier Out')], default="draft", string="Enter Exit Allowed", tracking=True)
    # USER_ID AND EMPLOYEE RELATION
    @api.depends('permit_issuer_id')
    def _compute_related_employee(self):
        for permission in self:
            if permission.permit_issuer_id:
                employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
                permission.related_employee_id = employee.id
            else:
                permission.related_employee_id = False

    # AUTO RECORD CODING SYSTEM
    @api.model
    def create(self, vals):
        if vals.get('permission_code', 'New') == 'New':
            vals['permission_code'] = self.env['ir.sequence'].next_by_code('transportation_sequence') or 'New'
        return super(VehicleExitPermit, self).create(vals)

    # RUNNING BUTTON
    def action_running_permission(self):
        security_vehicle_exit_obj = self.env['osoul.transportation.consent']
        
        for permit in self:
            values = {
                'permit_issuer_id': permit.permit_issuer_id.id,
                'related_employee_id': permit.related_employee_id.id,
                'employment_no_id': permit.employment_no_id,
                'department_id': permit.department_id.id,
                'driver_id': permit.driver_id.id,
                'emp_id_no': permit.emp_id_no,
                'emp_department_id': permit.emp_department_id.id,
                'country_id': permit.country_id.id,
                
            }
            self.state = "running"
            security_vehicle_exit_obj.create(values)
        

        
    
    