from odoo import fields, models

class TransportationDriver(models.Model):
    _name = 'osoul.transportation.driver'
    _description = 'Driver'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Many2one(
        string="Driver Name",
        comodel_name="hr.employee",
        ondelete="restrict",
        required=True,
        tracking=True,
    )
    emp_id_no = fields.Char(
        related="name.employment_no", string="Employee ID", tracking=True
        
    )
    country_id = fields.Many2one(related='name.country_id',string='Nationality',readonly=True ,tracking=True)
    emp_department_id = fields.Many2one(
        related="name.department_id",
        string="Department",
        readonly=True,
        store=True,
        tracking=True,
    )
    in_out_state = fields.Selection([('draft','Draft'),('inside_osoul','Inside Osoul'),('outside_osoul','Out Osoul')], string="InOut Status", default="draft")
    license_number = fields.Char(string="License Number", required=True)
    phone = fields.Char(string="Phone Number")
    email = fields.Char(string="Email")
    vehicle_ids = fields.One2many('transportation.vehicle', 'driver_id', string="Assigned Vehicles")

    driver_image = fields.Binary(string="Driver Image", attachment=True)
    address = fields.Text(string="Address")
    active = fields.Boolean(string="Active", default=True)
