from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError
from datetime import datetime
from odoo.exceptions import UserError
import random


class TransportationConsent(models.Model):
    _name = 'osoul.transportation.consent'
    _description = 'Vehicle Exit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "related_employee_id"

    
    permit_issuer_id = fields.Many2one('res.users', string="Permit Issuer")
    related_employee_id = fields.Many2one('hr.employee', string="Related Employee")
    employment_no_id = fields.Char(string="Employment No")
    department_id = fields.Many2one('hr.department', string="Department")
    driver_id = fields.Many2one('osoul.transportation.driver', string="Assigned Driver")
    emp_id_no = fields.Char(string="Employee ID")
    emp_department_id = fields.Many2one('hr.department', string="Department")
    country_id = fields.Many2one('res.country', string='Nationality')
    
    # GOING OUT PERMISSION
    def action_allowed_exit(self):
        # self.enter_exit_permission = "allowed_exit"
        security_vehicle_exit_obj = self.env['osoul.security.vehicle.exit']
        
        for permit in self:
            values = {
                
                'related_employee_id': permit.related_employee_id.id,
                'employment_no_id': permit.employment_no_id,
                'department_id': permit.department_id.id,
                'driver_id': permit.driver_id.id,
                'emp_id_no': permit.emp_id_no,
                'emp_department_id': permit.emp_department_id.id,
                'country_id': permit.country_id.id,
                
            }
            
            security_vehicle_exit_obj.create(values)
    