import requests
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OsoulOccuViolation(models.Model):
    _name = 'osoul.occu.violation'
    _description = 'Occupational Violation Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'emp_name_id'

    emp_name_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name")
    emp_department_id = fields.Many2one(related='emp_name_id.department_id', string="Department", readonly=True)
    emp_phone = fields.Char(related='emp_name_id.mobile_phone', string="Employee Phone", readonly=True)
    emp_manager = fields.Many2one(related='emp_name_id.parent_id', string="Manager")
    manager_phone = fields.Char(related='emp_manager.mobile_phone', string="Manager Phone")
    violation_no = fields.Char(string="Violation No", readonly=True, copy=False)
    violation_type = fields.Many2many(comodel_name="osoul.occu.violation.type", string="Violation Type")
    violation_date = fields.Datetime(string="Violation Date/Time", required=True, default=fields.Datetime.now)
    violation_site = fields.Many2one(comodel_name="osoul.occu.site", string="Violtion Site", ondelete='cascade')
    violation_location = fields.Many2one(comodel_name="osoul.occu.location", string="Violation Location", domain="[('site_id','=',violation_site)]", ondelete='cascade')
    violation_impact_summary = fields.Text(string="Violation Impact", compute="_compute_violation_impact", readonly=True)
    attachment = fields.Boolean()
    attachment_ids = fields.Many2many(comodel_name="ir.attachment", relation="osoul_occu_violation_ir_attachment_rel", string="Attachments")
    violation_issuer = fields.Many2one(comodel_name="res.users", string="Violation Issuer", default=lambda self: self.env.user, readonly=True)
    recommendation = fields.Text(string="Recommendation")
    signature = fields.Binary(string="Signature", help="Employee acknowledgment signature for receiving the violation ticket.")
    confirmed_date = fields.Datetime(string="Date/Time", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('confirmed', 'Confirmed')
    ], default="draft", string="State", readonly=True)

    @api.depends('violation_type')
    def _compute_violation_impact(self):
        for record in self:
            record.violation_impact_summary = '\n'.join(record.violation_type.mapped('impact'))

    @api.constrains('violation_date', 'confirmed_date')
    def _check_violation_dates(self):
        for record in self:
            if record.confirmed_date and record.confirmed_date < record.violation_date:
                raise ValidationError(_("Confirmation date cannot be earlier than the violation date."))

    @api.onchange('violation_type', 'violation_site')
    def _onchange_violation_fields(self):
        for record in self:
            if record.violation_site:
                record.violation_location = False

    def action_submitted(self):
        for record in self:
            if not record.violation_no:
                record.violation_no = self.env['ir.sequence'].next_by_code('osoul.occu.violation') or _('New')
            record.state = "submitted"
            record.message_post(body=_("Violation has been submitted."))
            record._send_whatsapp_message_submission()

    def action_confirmed(self):
        for record in self:
            if not record.signature:
                raise ValidationError(_("Violation Ticket has not been signed yet."))
            record.state = "confirmed"
            record.confirmed_date = fields.Datetime.now()
            record.message_post(body=_("Violation has been confirmed and acknowledged."))
            record._send_whatsapp_message_confirmation()

    def _send_whatsapp_message_submission(self):
        for record in self:
            instance_id = "instance103098"
            token = "dm86hbcidw154pdh"
            api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            site_label = record.violation_site.name if record.violation_site else 'N/A'
            location_label = record.violation_location.name if record.violation_location else 'N/A'

            contacts = [
                (record.emp_phone, record.emp_name_id.name),
                (record.manager_phone, record.emp_manager.name if record.emp_manager else ''),
            ]
            for phone, person_name in contacts:
                if not phone:
                    continue
                message_body = f"""
Hello {person_name},

A new Violation has been Submitted!
Violation No: {record.violation_no or 'N/A'}
Site: {site_label}
Location: {location_label}
Date/Time: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()

                payload = {'token': token, 'to': phone, 'body': message_body}
                try:
                    response = requests.post(api_url, json=payload, timeout=10)
                    if response.status_code != 200:
                        raise ValidationError(_("Failed to send WhatsApp message to %s. Response: %s") % (person_name, response.text))
                except requests.RequestException as e:
                    raise ValidationError(_("Error while sending WhatsApp message to %s: %s") % (person_name, str(e)))

    def _send_whatsapp_message_confirmation(self):
        for record in self:
            instance_id = "instance103098"
            token = "dm86hbcidw154pdh"
            api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            site_label = record.violation_site.name if record.violation_site else 'N/A'
            location_label = record.violation_location.name if record.violation_location else 'N/A'

            contacts = [
                (record.emp_phone, record.emp_name_id.name),
                (record.manager_phone, record.emp_manager.name if record.emp_manager else ''),
            ]
            for phone, person_name in contacts:
                if not phone:
                    continue
                message_body = f"""
Hello {person_name},

Your Violation has been Confirmed!
Violation No: {record.violation_no or 'N/A'}
Site: {site_label}
Location: {location_label}
Confirmed Date/Time: {record.confirmed_date.strftime('%Y-%m-%d %H:%M:%S')}
""".strip()

                payload = {'token': token, 'to': phone, 'body': message_body}
                try:
                    response = requests.post(api_url, json=payload, timeout=10)
                    if response.status_code != 200:
                        raise ValidationError(_("Failed to send WhatsApp message to %s. Response: %s") % (person_name, response.text))
                except requests.RequestException as e:
                    raise ValidationError(_("Error while sending WhatsApp message to %s: %s") % (person_name, str(e)))
                

class OsoulOccuViolationType(models.Model):
    _name = 'osoul.occu.violation.type'
    _description = 'Occupational Violation Type'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # FIELDS.
    name = fields.Char(string="Violation Type", required=True, tracking=True, help="Specify the name of the violation type.")
    impact = fields.Text(string="Violation Impact", required=True, tracking=True, help="Describe the potential or actual impact of this type of violation.")