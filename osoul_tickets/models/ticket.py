import requests
import logging
import json
from odoo import models, fields, api, _
from odoo import http
from odoo.exceptions import ValidationError
from google.oauth2 import service_account
from google.auth.transport.requests import Request
_logger = logging.getLogger(__name__)

class Ticket(models.Model):
    _name = 'ticket.job.order'
    _description = 'Ticket Job Order'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "job_order_sequence"



    def action_whatsapp(self):
        if not self.requester_no:
            raise ValidationError(_("Missing Phone Number"))
        msg = 'hi %s' % self.unit_head.name
        whatsapp_api_url = f"https://api.whatsapp.com/send?phone=%s&text=%s" % (self.requester_no,msg)
        
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': whatsapp_api_url
        }



    def generate_firebase_token(self, service_account_json: str) -> str:
        """
        Generate an OAuth2 Bearer Token using a Firebase Service Account JSON.

        Args:
            service_account_json (str): Path to the Firebase service account JSON file.

        Returns:
            str: A valid OAuth2 Bearer Token.
        """
        try:
            # Log the file path being used
            _logger.info(f"Looking for service account JSON at: {service_account_json}")

            # Load the service account JSON file
            with open(service_account_json, 'r') as file:
                service_account_data = json.load(file)

            # Extract useful fields for debugging
            project_id = service_account_data.get("project_id")
            _logger.info(f"Generating token for project: {project_id}")

            # Generate OAuth2 Bearer Token
            credentials = service_account.Credentials.from_service_account_info(
                service_account_data,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            credentials.refresh(Request())  # Refresh to get a new token
            return credentials.token
        except FileNotFoundError:
            _logger.error(f"Service account JSON file not found: {service_account_json}")
            raise ValidationError(_("Service account JSON file not found. Please check the path and try again."))
        except json.JSONDecodeError:
            _logger.error("Invalid JSON format in service account file.")
            raise ValidationError(_("Invalid JSON format in service account file."))
        except Exception as e:
            _logger.exception("Failed to generate Firebase token.")
            raise ValidationError(f"Failed to generate Firebase token: {str(e)}")

    def send_fcm_notification(self, device_token: str, title: str, body: str, bearer_token: str):
        """
        Sends a notification using Firebase Cloud Messaging (FCM).

        Args:
            device_token (str): The recipient's Firebase device token.
            title (str): Notification title.
            body (str): Notification body.
            bearer_token (str): OAuth2 Bearer Token for Firebase authentication.
        """
        # FCM API URL
        url = "https://fcm.googleapis.com/v1/projects/tekno-app/messages:send"

        # Construct the payload
        payload = {
            "message": {
                "token": device_token,
                "notification": {
                    "title": title,
                    "body": body
                }
            }
        }

        # Set headers
        headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

        try:
            # Make the POST request to FCM
            response = requests.post(url, headers=headers, json=payload)

            # Log the response for debugging
            _logger.info("FCM response: %s", response.text)

            # Check the response status code
            if response.status_code == 200:
                _logger.info("Notification sent successfully.")
                return _("Notification sent successfully.")
            else:
                _logger.error("Failed to send notification: %s", response.text)
                return _("Failed to send notification: %s") % response.text
        except Exception as e:
            _logger.exception("An error occurred while sending FCM notification.")
            raise ValidationError(_("An error occurred: %s") % str(e))

    def notify_user(self, user_id: int, title: str, body: str):
        """
        Send a Firebase Cloud Messaging (FCM) notification to a specific user.

        Args:
            user_id (int): The ID of the target user in res.users.
            title (str): Notification title.
            body (str): Notification body.
        """
        # Path to the Firebase service account JSON file
        service_account_json = "/opt/odoo/odoo/osoul_addons/osoul_tickets/menu/service_account.json"

        try:
            # Fetch the user's device token
            user = self.env['res.users'].browse(6)
            if not user or not user.token:
                raise ValidationError(_("The user does not have a valid Firebase token."))

            device_token = user.token

            # Generate Bearer Token
            bearer_token = self.generate_firebase_token(service_account_json)

            # Send the notification
            result = self.send_fcm_notification(device_token, title, body, bearer_token)
            _logger.info("Notification result for user %s: %s", 6, result)
            return result
        except ValidationError as e:
            _logger.error("Validation error: %s", e)
            raise
        except Exception as e:
            _logger.exception("An error occurred while sending notification to user %s.", 6)
            raise ValidationError(_("An error occurred: %s") % str(e))

    def notify_unit_members(self, unit: str, title: str, body: str):
        """
        Notify all users in the selected unit.

        Args:
            unit (str): The unit to notify members of.
            title (str): Notification title.
            body (str): Notification body. 
        """
        service_account_json = "/opt/odoo/odoo/osoul_addons/osoul_tickets/menu/service_account.json"

        try:
            # Generate Bearer Token
            bearer_token = self.generate_firebase_token(service_account_json)

            # Fetch users in the selected unit
            users = self.env['res.users'].search([('responsible_unit', '=', unit), ('token', '!=', False)])
            if not users:
                _logger.warning(f"No users found in the unit: {unit} with valid tokens.")
                return

            # Send notification to each user
            for user in users:
                self.send_fcm_notification(user.token, title, body, bearer_token)
                _logger.info(f"Notification sent to user {user.id} ({user.name}).")
        except Exception as e:
            _logger.error(f"Error sending notifications to unit {unit}: {e}")
            raise ValidationError(_("Error sending notifications to unit %s: %s") % (unit, str(e)))


    def trigger_fcm_notification(self):
        """
        Test action to send notification using Firebase Cloud Messaging.
        """
        # Path to the Firebase service account JSON file
        service_account_json = "/opt/odoo/odoo/osoul_addons/osoul_tickets/menu/service_account.json"

        try:
            # Generate Bearer Token
            bearer_token = self.generate_firebase_token(service_account_json)

            # Example: Sending a notification to a specific user for a ticket
            ticket = self.env['ticket.job.order'].browse(1)  # Replace 1 with the actual ticket ID
            user_id = 6  # Replace with the actual user ID
            title = "Important Update"
            body = "Your job order has been updated."

            # Notify the user
            ticket.notify_user(user_id, title, body)
        except Exception as e:
            _logger.exception("An error occurred while triggering the FCM notification.")
            raise ValidationError(_("An error occurred: %s") % str(e))


    
    responsible_unit = fields.Selection([
        ('networks', 'Networks'),
        ('systems', 'Systems'),
        ('technical_support', 'Technical Support'),
        ('developers', 'Developers'),
        ('operation', 'Operation'),
        ('information_technology_office', 'Information Technology Office')
    ], string='Unit', required=True)


    job_order_sequence = fields.Char(
        string='Job Order Sequence',
        store=True,
        readonly=True,
        copy=False,
        help="Unique sequence generated only once when a job order is created."
    )

    unit_head = fields.Many2one('res.users', string="Unit Head", readonly=True)

    _sql_constraints = [
        ('job_order_sequence_unique', 'unique(job_order_sequence)',
         'The Job Order Sequence must be unique.')
    ]

    @api.model
    def create(self, vals):
        # Generate sequence if not provided
        if not vals.get('job_order_sequence'):
            vals['job_order_sequence'] = self.env['ir.sequence'].next_by_code('ticket.job.order')
            _logger.info(f"Generated job_order_sequence: {vals['job_order_sequence']} for Ticket")

        # Set unit head based on responsible_unit
        if vals.get('responsible_unit'):
            vals['unit_head'] = self._get_unit_head(vals['responsible_unit'])
        return super(Ticket, self).create(vals)

    def write(self, vals):
        # Update unit head if responsible_unit changes
        if 'responsible_unit' in vals:
            vals['unit_head'] = self._get_unit_head(vals['responsible_unit'])
        return super(Ticket, self).write(vals)

    @api.onchange('responsible_unit')
    def _onchange_responsible_unit(self):
        """Set unit head based on the selected responsible unit."""
        if self.responsible_unit:
            self.unit_head
            self._get_unit_head(self.responsible_unit)
        else:
            self.unit_head = False

    def _get_unit_head(self, unit):
        """Utility method to get the unit head based on the unit."""
        unit_heads = {
            'networks': self.env.ref('osoul_tickets.user_network_head', raise_if_not_found=False).id,
            'systems': self.env.ref('osoul_tickets.user_systems_head', raise_if_not_found=False).id,
            'technical_support': self.env.ref('osoul_tickets.user_technical_support_head', raise_if_not_found=False).id,
            'developers': self.env.ref('osoul_tickets.user_developers_head', raise_if_not_found=False).id,
            'operation': self.env.ref('osoul_tickets.user_operation_head', raise_if_not_found=False).id,
            'information_technology_office': self.env.ref('osoul_tickets.user_information_head', raise_if_not_found=False).id,
        }
        return unit_heads.get(unit)
    

    issue_location_id = fields.Many2one('osoul.tickets.settings',string='Issue Location', required=True, ondelete='restrict', tracking=True)
    approval_id = fields.Many2one('ticket.approval', string="Related", readonly=True)
    job_order_id = fields.Many2one('project.task', string='Job Order', readonly=True)
    employee_id = fields.Many2one(comodel_name="hr.employee",
                                  string="Requester Name", 
                                  ondelete='restrict', required=True, tracking=True)
    hold_reason = fields.Char(string='Hold Reason')
    assignees_name = fields.Many2many('osoul.tickets.team.member', string='Technician Assignees',readonly=True)
    employement_no = fields.Char(related='employee_id.employment_no', string="Requester Id", tracking=True)
    requester_no = fields.Char(string="Contact No", tracking=True)
    department = fields.Many2one(related='employee_id.department_id', string="Requester Department", tracking=True, store=True)
    solution = fields.Text(string='Solution')
    description = fields.Text(string='Issue Description', required=True)
    # Timing Info
    ticket_date = fields.Datetime(string="Job Order Date", default=fields.Datetime.now,readonly=True)
    under_progress_date = fields.Datetime(string='Under Progress Date',readonly=True)
    hold_date = fields.Datetime(string='Hold Date',readonly=True)
    finish_date = fields.Datetime(string='Finish Date',readonly=True)
    time_difference = fields.Integer(string="Time Taken", compute='_compute_time_difference', store=True, readonly=True)
    time_to_start = fields.Integer(string="Time to Under Progress", compute='_compute_time_to_start',store=True, readonly=True)

    @api.depends('ticket_date', 'under_progress_date')
    def _compute_time_to_start(self):
        for record in self:
            if record.ticket_date and record.under_progress_date:
                time_diff = record.under_progress_date - record.ticket_date
                record.time_to_start = int(time_diff.total_seconds() / 60)  # Convert to minutes
            else:
                record.time_to_start = 0

    @api.depends('under_progress_date', 'finish_date')
    def _compute_time_difference(self):
        for record in self:
            if record.under_progress_date and record.finish_date:
                time_diff = record.finish_date - record.under_progress_date
                record.time_difference = int(time_diff.total_seconds() / 60)  # Convert to minutes
            else:
                record.time_difference = 0

    responsible_unit = fields.Selection([
        ('networks', 'Networks'),
        ('systems', 'Systems'),
        ('technical_support', 'Technical Support'),
        ('developers', 'Developers'),
        ('operation', 'Operation'),
        ('information_technology_office', 'Information Technology Office')
    ], string='Unit', required=True)
    
    
    unit_head = fields.Many2one('res.users', string="Unit Head", readonly=True)
    @api.onchange('responsible_unit')
    def _onchange_responsible_unit(self):
        """Set unit head based on the selected responsible unit."""
        if self.responsible_unit:
            unit_heads = {
                'networks': self.env.ref('osoul_tickets.user_network_head', raise_if_not_found=False),
                'systems': self.env.ref('osoul_tickets.user_systems_head', raise_if_not_found=False),
                'technical_support': self.env.ref('osoul_tickets.user_technical_support_head', raise_if_not_found=False),
                'developers': self.env.ref('osoul_tickets.user_developers_head', raise_if_not_found=False),
                'operation': self.env.ref('osoul_tickets.user_operation_head', raise_if_not_found=False),
                'information_technology_office': self.env.ref('osoul_tickets.user_information_head', raise_if_not_found=False),
            }
            self.unit_head = unit_heads.get(self.responsible_unit, False)
        else:
            self.unit_head = False

    location = fields.Selection([('osoul_poultry', 'Osoul Poultry'),
                                 ('osoul_hatchery', 'Osoul Hatchery'),
                                 ('osoul_jeddah', 'Osoul Jeddah'),
                                 ('osoul_jizan', 'Osoul Jizan'),
                                 ('osoul_abha', 'Osoul Abha')], default='osoul_poultry', string="Site", required=True, tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('job_created', 'Job Created'),
        ('canceled', 'Canceled'),
        ('hold', 'Hold'),
        ('under_progress', 'Under Progress'),
        ('done', 'Done'),
    ], default='draft', string='Status', track_visibility='onchange')

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
        ('urgent', 'Urgent')
    ], default='medium', string='Priority', tracking=True)

    def action_create_job_order(self):
        for record in self:
            # Generate sequence if not provided
            if not record.job_order_sequence:
                _logger.warning(f"Job Order Sequence is missing for Ticket ID {record.id} during job order creation.")
                continue

            # Determine the unit head based on the responsible unit
            unit_heads = {
                'networks': self.env.ref('osoul_tickets.user_network_head', raise_if_not_found=False),
                'systems': self.env.ref('osoul_tickets.user_systems_head', raise_if_not_found=False),
                'technical_support': self.env.ref('osoul_tickets.user_technical_support_head', raise_if_not_found=False),
                'developers': self.env.ref('osoul_tickets.user_developers_head', raise_if_not_found=False),
                'operation': self.env.ref('osoul_tickets.user_operation_head', raise_if_not_found=False),
                'information_technology_office': self.env.ref('osoul_tickets.user_information_head', raise_if_not_found=False),
            }
            record.unit_head = unit_heads.get(record.responsible_unit)

            # Create a job approval record
            approval_record = self.env['ticket.approval'].create({
                'ticket_id': record.id,
                'job_order_sequence': record.job_order_sequence,
                'description': record.description,
                'responsible_unit': record.responsible_unit,
                'location': record.location,
                'employee_id': record.employee_id.id,
                'requester_no': record.requester_no,
                'priority': record.priority,
                'ticket_date': record.ticket_date,
                'unit_head': record.unit_head.id,
                'issue_location_id': record.issue_location_id.id,
            })
            record.approval_id = approval_record.id

            # Notify all unit members
            try:
                self.notify_unit_members(record.responsible_unit, f"{record.job_order_sequence}", f"{record.description}")
            except Exception as e:
                _logger.error(f"Error notifying unit members for Ticket ID {record.id}: {e}")

            # Notify users via mail activity if there is an assignee
            if approval_record.assignees_name:
                activity_user = approval_record.assignees_name[0].id
                activity_type = self.env.ref('mail.mail_activity_data_todo').id
                self.env['mail.activity'].create({
                    'activity_type_id': activity_type,
                    'note': "A job order has been created for this ticket.",
                    'res_model_id': self.env['ir.model']._get('ticket.approval').id,
                    'res_id': approval_record.id,
                    'user_id': activity_user,
                })
            else:
                _logger.warning(f"No assignees found for Approval ID {approval_record.id}")
            record.state = 'job_created'

            # Return a confirmation message
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': _('Good Job Order Created'),
                    'type': 'rainbow_man',
                }
            }


    def action_cancel(self):
        for record in self:
            record.state = 'canceled'
            _logger.info(f"Setting state to 'canceled' for Ticket ID: {record.id}")
            
            if record.approval_id:
                try:
                    record.approval_id.state = 'canceled'
                    _logger.info(f"Approval ID {record.approval_id.id} state set to 'canceled'")
                except Exception as e:
                    _logger.error(f"Failed to update state on approval_id {record.approval_id.id}: {e}")
            else:
                _logger.warning(f"No related approval_id found for Ticket ID: {record.id}")

    