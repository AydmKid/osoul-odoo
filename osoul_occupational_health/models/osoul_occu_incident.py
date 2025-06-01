import requests
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OsoulOccuIncident(models.Model):
    _name = "osoul.occu.incident"
    _description = "Occupational Health and Safety Incident"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(string="Incident Name", tracking=True)
    incident_no = fields.Char(string="Incident No", readonly=True)
    incident_date = fields.Datetime(string="Incident Date/Time", default=fields.Datetime.now, tracking=True)
    reported_by = fields.Many2one(comodel_name="hr.employee", string="Reported By", tracking=True)
    department_id = fields.Many2one(related='reported_by.department_id', string="Department", readonly=True)
    manager_id = fields.Many2one(related='department_id.manager_id', string="Manager", readonly=True)
    incident_type = fields.Selection([
        ('accident', 'Accident'),
        ('near_miss', 'Near Miss'),
        ('property_damage', 'Property Damage'),
        ('injury', 'Injury'),
        ('fatality', 'Fatality')],
        string="Incident Type", tracking=True)
    incident_site_id = fields.Many2one(
        comodel_name="osoul.occu.site", 
        string="Incident Site", 
        ondelete="cascade",
        help="The site where the incident occurred."
    )
    incident_location_id = fields.Many2one(
        comodel_name="osoul.occu.location",
        string="Incident Location",
        domain="[('site_id', '=', incident_site_id)]",
        ondelete="cascade",
        help="The specific location within the site."
    )
    injuries = fields.Boolean(string="Any Injuries?", help="Check if the incident resulted in any injuries.", tracking=True)
    injury_people = fields.Many2many(comodel_name="hr.employee", string="Injured People")
    injury_details = fields.Text(string="Injury Details", help="Describe the injuries, if any.", tracking=True)
    damages = fields.Text(string="Damages", help="Describe property or equipment damages, if any.", tracking=True)
    description = fields.Text(string="Incident Description", help="Describe the incident in detail.")
    root_cause = fields.Text(string="Root Cause Analysis", help="Explain the root cause of the incident.")
    corrective_actions = fields.Text(string="Corrective Actions", help="Actions taken or planned to prevent recurrence.")
    witness_ids = fields.Many2many(
        comodel_name="hr.employee",
        relation="osoul_occu_incident_report_witness_rel",
        string="Witnesses",
        help="Any employees who witnessed the incident."
    )
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment",
        relation="osoul_occu_incident_report_attachment_rel",
        string="Attachments",
        help="Add any evidence or supporting documentation."
    )
    investigator_id = fields.Many2one(comodel_name="res.users", string="Investigator", readonly=True)
    Investigation_start_date = fields.Datetime(string="Investigation Start", readonly=True)
    Investigation_ends_date = fields.Datetime(string="Investigation Ends", readonly=True)
    investigator_duration = fields.Char(string="Investigation Duration", readonly=True)
    incident_close_date = fields.Datetime(string="Incident Closed Date", readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('investigation', 'Under Investigation'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')],
        default='draft', string="Status", tracking=True)

    @api.constrains('incident_date')
    def _check_incident_date(self):
        for record in self:
            if record.incident_date and record.incident_date > fields.Datetime.now():
                raise ValidationError(_("Incident date cannot be in the future."))

    @api.onchange('incident_site_id')
    def onchange_violation_site(self):
        for record in self:
            if record.incident_site_id:
                record.incident_location_id = False

    def action_submitted(self):
        """Mark the incident as 'Submitted' and send WhatsApp message to the reporter."""
        for record in self:
            record.incident_no = self.env['ir.sequence'].next_by_code('osoul.occu.incident') or _('New')
            record.state = "submitted"
            # Call the helper method to send WhatsApp to the reporter
            record._send_whatsapp_message_reporter()

    def action_investigate(self):
        """Move the incident to 'Under Investigation' state."""
        for record in self:
            record.investigator_id = self.env.user
            record.Investigation_start_date = fields.Datetime.now()
            record.state = 'investigation'
            record.message_post(body=_("Incident is now under investigation."))

    def action_resolve(self):
        """Mark the incident as resolved, typically after implementing corrective actions."""
        for record in self:
            record.Investigation_ends_date = fields.Datetime.now()
            if record.Investigation_start_date:
                duration = record.Investigation_ends_date - record.Investigation_start_date
                days = duration.days
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _seconds = divmod(remainder, 60)
                record.investigator_duration = f"{days}d {hours}h {minutes}m"
            record.state = 'resolved'
            record.message_post(body=_("Incident has been resolved with corrective actions."))

    def action_close(self):
        """Close the incident, no further actions needed."""
        for record in self:
            record.incident_close_date = fields.Datetime.now()
            record.state = 'closed'
            record.message_post(body=_("Incident is closed. No further actions required."))

    def _send_whatsapp_message_reporter(self):
        """Send a WhatsApp message to the 'reported_by' employee when the incident is submitted."""
        for record in self:
            # If no reporter is set, or if the reporter doesn't have a phone, skip
            if not record.reported_by or not record.reported_by.mobile_phone:
                continue

            instance_id = "instance103098"  # UltraMsg instance ID
            token = "dm86hbcidw154pdh"      # UltraMsg API token
            api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

            reporter_phone = record.reported_by.mobile_phone
            site_label = record.incident_site_id.name if record.incident_site_id else 'N/A'
            location_label = record.incident_location_id.name if record.incident_location_id else 'N/A'

            message_body = f"""
Hello {record.reported_by.name},

Your incident has been submitted successfully!
Incident No: {record.incident_no or 'N/A'}
Site: {site_label}
Location: {location_label}
Date/Time: {record.incident_date.strftime('%Y-%m-%d %H:%M:%S') if record.incident_date else 'N/A'}
""".strip()

            payload = {
                'token': token,
                'to': reporter_phone,
                'body': message_body
            }

            try:
                response = requests.post(api_url, json=payload, timeout=10)
                if response.status_code != 200:
                    raise ValidationError(_(
                        "Failed to send WhatsApp message to {}. Response: {}"
                    ).format(record.reported_by.name, response.text))
            except requests.RequestException as e:
                raise ValidationError(_(
                    "Error while sending WhatsApp message to {}: {}"
                ).format(record.reported_by.name, str(e)))