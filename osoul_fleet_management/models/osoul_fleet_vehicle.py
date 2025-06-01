from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
import datetime
import logging
import base64
import io
import qrcode
from odoo.addons.bus.models.bus import dispatch

_logger = logging.getLogger(__name__)

class OsoulFleetVehicle(models.Model):
    _name = 'osoul.fleet.vehicle'
    _description = 'Fleet Vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'license_plate'

    # Fields
    license_plate = fields.Char(string="License Plate", compute="_compute_license_plate", store=True, tracking=True, index=True)
    plate_letters = fields.Char(string="Plate Letters", size=6, tracking=True)
    plate_numbers = fields.Char(string="Plate Numbers", size=4, tracking=True)
    manufacture_year = fields.Integer(string="Manufacture Year", tracking=True, 
                                      help="Year the vehicle was manufactured.")
    work_role = fields.Many2one(comodel_name="osoul.fleet.work.role", string="Work Role", tracking=True)
    weight = fields.Integer(string="Weight (kg)", tracking=True)
    plate_type = fields.Many2one("osoul.fleet.plate.type", string="Plate Type", tracking=True)
    category = fields.Many2one(comodel_name="osoul.fleet.category", string="Category", tracking=True)
    brand = fields.Many2one(comodel_name="osoul.fleet.brand", string="Brand", tracking=True)
    classification = fields.Many2one(comodel_name="osoul.fleet.classification", string="Classification", tracking=True)
    fuel_type = fields.Selection(
        [('gazoline', 'Gasoline'), ('diesel', 'Diesel')],
        string="Fuel Type",
        tracking=True,
        default="gazoline",
        help="The type of fuel used by this vehicle.")
    owner = fields.Many2one(comodel_name="osoul.fleet.owner", string="Owner", tracking=True)
    work_location = fields.Many2one(comodel_name="osoul.fleet.work.location", string="Work Location", tracking=True)
    serial_no = fields.Char(string="Serial No", tracking=True)
    chassis_no = fields.Char(string="Chassis No", tracking=True)
    qr_code = fields.Image(string="QR Code", compute="_compute_qr_code", store=True)
    active = fields.Boolean(string="Active", default=True, tracking=True)
    activation = fields.Selection([('active', 'Active'), ("not_active", "Not Active")], default="active", tracking=True, readonly=True)

    # Constraints-Unique License Plate
    _sql_constraints = [
        ('unique_license_plate', 'unique(license_plate)', 'The license plate must be unique.'),
    ]

    # Onchange
    @api.onchange('plate_letters')
    def _onchange_plate_letters(self):
        if self.plate_letters:
            self.plate_letters = self.plate_letters.upper()

    # Compute License Plate
    @api.depends('plate_letters', 'plate_numbers')
    def _compute_license_plate(self):
        for record in self:
            record.license_plate = f"{record.plate_letters or ''}-{record.plate_numbers or ''}".strip('-')

    # Constraints
    @api.constrains('manufacture_year')
    def _check_manufacture_year(self):
        current_year = datetime.date.today().year
        for record in self:
            if record.manufacture_year and (record.manufacture_year < 1900 or record.manufacture_year > current_year):
                _logger.warning(
                    f"Invalid manufacture year: {record.manufacture_year} for vehicle {record.id}"
                )
                raise ValidationError(
                    _("The manufacture year must be between 1900 and the current year.")
                )

    @api.constrains('plate_numbers')
    def _check_plate_numbers(self):
        for record in self:
            if record.plate_numbers and not record.plate_numbers.isdigit():
                _logger.warning(f"Non-numeric plate numbers: {record.plate_numbers} for vehicle {record.id}")
                raise ValidationError(_("Plate Numbers must contain only numeric characters."))

    # Compute QR Code
    @api.depends('chassis_no')
    def _compute_qr_code(self):
        for record in self:
            if record.chassis_no:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.chassis_no)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_image_base64 = base64.b64encode(buffered.getvalue())
                record.qr_code = qr_image_base64
            else:
                record.qr_code = False

    # Button to Generate QR Code
    def action_generate_qr_code(self):
        for record in self:
            if record.chassis_no:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(record.chassis_no)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                qr_image_base64 = base64.b64encode(buffered.getvalue())
                record.qr_code = qr_image_base64
            else:
                raise ValidationError(_("Chassis No is required to generate a QR code."))
            

    def action_active(self):
        for record in self:
            record.activation = 'active'

    
    def action_not_active(self):
        for record in self:
            record.activation = 'not_active'



from odoo import models, api

class RealTimeExample(models.Model):
    _name = 'real.time.example'

    @api.model
    def send_update(self, message):
        dispatch(
            self.env.cr,  # Current cursor
            'real.time.channel',  # Channel name
            {'message': message}  # Data to send
        )

def write(self, vals):
    result = super(RealTimeExample, self).write(vals)
    self.send_update("Record updated!")
    return result

