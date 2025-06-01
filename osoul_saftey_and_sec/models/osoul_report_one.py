import requests
import logging
import json
from odoo import models, fields, api, _
from odoo import http
from odoo.exceptions import ValidationError
from google.oauth2 import service_account
from google.auth.transport.requests import Request
_logger = logging.getLogger(__name__)

class OsoulReportOne(models.Model):
    _name = "osoul.report.one"  
    _description = "Report One"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "inspection_type"

    inspection_type = fields.Selection([
        ('machines', 'Machines'),
        ('extinguishers', 'Extinguishers'),
        ('fire_boxes', 'Fire Boxes'),
        ('outlet_panels', 'Outlet Panels'),
        ('emergency_exits', 'Emergency Exits'),
        ('fire_alarm_panel', 'Fire Alarm Panel'),
    ], string="Examines Type", required=True)
    time = fields.Datetime(string="Time", required=True)
    location = fields.Char(string="Location")
    machine = fields.Char(string="Machine Name")
    type_of_extinguisher = fields.Char(string="Type of Extinguisher")
    examines = fields.Text(string="Examines")
    checking = fields.Text(string="Checking")
    reading = fields.Text(string="Reading")
    note = fields.Text(string="Note")
    attachments = fields.Binary(string="Attachments")

    report_time = fields.Datetime(string="Report Time",default=fields.Datetime.now,readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="Name", 
                                  ondelete='restrict', required=True, tracking=True)
    department = fields.Many2one(related='employee_id.department_id', string="Department", tracking=True, store=True)
    employement_no = fields.Char(related='employee_id.employment_no', string="Employee Id", tracking=True)
    job_order_sequence = fields.Char(
        string='Job Order Sequence',
        store=True,
        readonly=True,
        copy=False,
        help="Unique sequence generated only once when a job order is created."
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('job_created', 'Job Created'),
        ('canceled', 'Canceled'),
        ('under_progress', 'Under Progress'),
        ('done', 'Done'),
    ], default='draft', string='Status', track_visibility='onchange')



   

    