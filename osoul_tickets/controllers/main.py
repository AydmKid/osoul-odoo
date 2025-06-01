from odoo import http
from odoo.http import request, Response
import json
import logging
from datetime import datetime, timezone, timedelta
_logger = logging.getLogger(__name__)

class OsoulTicketsController(http.Controller):

    @http.route('/api/users/save_token', type='json', auth='user', methods=['POST'], csrf=False)
    def save_user_token(self):
        """
        Save the Firebase Cloud Messaging (FCM) token for the logged-in user.
        """
        try:
            # Log the incoming request for debugging
            _logger.info("Incoming request data: %s", request.jsonrequest)

            # Parse 'params' and get 'token'
            data = request.jsonrequest
            token = data.get('params', {}).get('token')  # Nested extraction from 'params'

            if not token:
                return {"result": {"status": "error", "message": "Token is required."}}

            # Fetch the logged-in user
            user = request.env.user
            if not user:
                return {"result": {"status": "error", "message": "User not authenticated."}}

            # Save the token to the 'token' field in res.users
            user.sudo().write({'token': token})
            return {"result": {"status": "success", "message": "Token saved successfully."}}
        except Exception as e:
            _logger.exception("Error saving token")
            return {"result": {"status": "error", "message": f"An error occurred: {str(e)}"}}



    @http.route('/api/send_notification', type='json', auth='public', methods=['POST'], csrf=False)
    def send_notification(self, **kwargs):
        """
        Send notification to the Flutter app.
        """
        try:
            title = kwargs.get('title')
            message = kwargs.get('message')
            user_id = kwargs.get('user_id')

            # Send notification logic (example for FCM or other APIs)
            # You can integrate this with Firebase Cloud Messaging (FCM) or other push services.
            
            # Example response
            response = {
                "status": "success",
                "message": f"Notification sent to user {user_id}",
            }
            return response
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def process_time(date_string):
        utc_time = datetime.fromisoformat(date_string).replace(tzinfo=timezone.utc)
        local_time = utc_time.astimezone()  # Convert to server local timezone
        print(f"UTC Time: {utc_time}, Local Time: {local_time}")

    @http.route('/api/tickets/create', type='json', auth='user', methods=['POST'], csrf=False)
    def create_ticket(self, **data):
        """Create a new ticket"""
        ticket = request.env['ticket.job.order'].sudo().create(data)
        return {'status': 'success', 'ticket_id': ticket.id}

    def handle_request(request):
        try:
            data = json.loads(request.body)
            params = data.get("params")
            if not params:
                return {"status": "error", "message": "Missing parameters"}
            id = params.get("id")
            state = params.get("state")
            field_value = params.get("field_value")
            if not id or not state or not field_value:
                return {"status": "error", "message": "Missing required fields"}
            # Proceed with processing...
        except Exception as e:
            return {"status": "error", "message": str(e)}


    @http.route('/api/tickets/update', type='json', auth='user', methods=['POST'], csrf=False)
    def update_ticket(self, **data):
        """Update an existing ticket and its related job order."""
        ticket_id = data.get('id')
        assignees_ids = data.get('assignees_name', [])[2] if data.get('assignees_name') else []

        ticket = request.env['ticket.approval'].sudo().browse(ticket_id)
        if ticket.exists():
            update_data = {}
            if assignees_ids:
                update_data['assignees_name'] = [(6, 0, assignees_ids)]
            
            # Update the ticket.approval record
            ticket.sudo().write(update_data)
            
            # Update the related ticket.job.order record, if exists
            if ticket.ticket_id:
                ticket.ticket_id.sudo().write({'assignees_name': [(6, 0, assignees_ids)]})
            
            return {'status': 'success'}
        else:
            return {'status': 'error', 'message': 'Ticket not found'}


    

    @http.route('/api/tickets/update_solution', type='json', auth='user', methods=['POST'], csrf=False)
    def update_ticket_solution(self, **data):
        """Update the solution of a specific ticket and its related job order."""
        try:
            ticket_id = data.get('id')
            solution = data.get('solution')

            # Validate input parameters
            if not ticket_id or not solution:
                return {'status': 'error', 'message': 'Missing parameters'}

            # Fetch the ticket.approval record
            ticket = request.env['ticket.approval'].sudo().browse(ticket_id)
            if ticket.exists():
                # Update the solution in ticket.approval
                ticket.sudo().write({'solution': solution})

                # Update the solution in the related ticket.job.order, if it exists
                if ticket.ticket_id:
                    ticket.ticket_id.sudo().write({'solution': solution})

                return {'status': 'success'}
            else:
                return {'status': 'error', 'message': 'Ticket not found'}
        except Exception as e:
            # Log the error for debugging
            _logger.error(f"Error updating ticket solution: {str(e)}")
            return {'status': 'error', 'message': f"Exception: {str(e)}"}



    @http.route('/api/assignees/get', type='json', auth='user', methods=['POST'], csrf=False)
    def get_assignees(self):
        """Fetch a list of available assignees with their IDs and names."""
        assignees = request.env['osoul.tickets.team.member'].sudo().search([])
        
        result = [{'id': assignee.id or -1, 'member_name': assignee.member_name.name or 'Unknown'} for assignee in assignees]
        
        return {'status': 'success', 'assignees': result}

    # @http.route('/api/assignees/get', type='json', auth='user', methods=['POST'], csrf=False)
    # def get_assignees_by_unit(self):
    #     """Fetch assignees for a specific unit."""
    #     data = request.jsonrequest  # Access the JSON payload

    #     unit_name = data.get('unit_name')  # Extract the unit_name parameter

    #     if not unit_name:
    #         return {
    #             'status': 'error',
    #             'message': 'Unit name is required.'
    #         }

    #     # Search for team members belonging to the specified unit
    #     assignees = request.env['osoul.tickets.team.member'].sudo().search([('unit_name', '=', unit_name)])

    #     if not assignees:
    #         return {
    #             'status': 'error',
    #             'message': f'No members found for unit: {unit_name}'
    #         }

    #     # Prepare the response data
    #     result = [
    #         {
    #             'id': assignee.member_name.id or -1,
    #             'member_name': assignee.member_name.name or 'Unknown'
    #         } for assignee in assignees
    #     ]

    #     return {
    #         'status': 'success',
    #         'unit_name': unit_name,
    #         'assignees': result
    #     }

        

    @http.route('/api/tickets/update_state_date', type='json', auth='user', methods=['POST'], csrf=False)
    def update_state_date(self, **data):
        """Update the state and corresponding date for a ticket in ticket.approval and ticket.job.order."""
        try:
            # Extract data from JSON-RPC request
            ticket_id = data.get('id')
            new_state = data.get('state')
            new_date_str = data.get('date')  # ISO 8601 datetime string

            # Validate input parameters
            if not ticket_id or not new_state or not new_date_str:
                return {'status': 'error', 'message': 'Missing parameters'}

            # Parse the provided datetime string
            try:
                new_date = datetime.strptime(new_date_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError as e:
                return {'status': 'error', 'message': f"Invalid date format: {str(e)}"}

            # Map the state to the corresponding date field
            state_date_map = {
                'under_progress': 'under_progress_date',
                'hold': 'hold_date',
                'done': 'finish_date',
            }

            date_field = state_date_map.get(new_state)
            if not date_field:
                return {'status': 'error', 'message': 'Invalid state'}

            # Prepare update data
            update_data = {'state': new_state}
            update_data[date_field] = new_date

            # Update ticket.approval
            ticket_approval = request.env['ticket.approval'].sudo().browse(ticket_id)
            if ticket_approval.exists():
                ticket_approval.write(update_data)
                _logger.info(f"Updated ticket.approval ID {ticket_id} with state {new_state} and date {new_date}")

                # Check if there is a related ticket.job.order
                related_job_order = request.env['ticket.job.order'].sudo().search([('approval_id', '=', ticket_approval.id)], limit=1)
                if related_job_order.exists():
                    related_job_order.write(update_data)
                    _logger.info(f"Updated related ticket.job.order ID {related_job_order.id} with state {new_state} and date {new_date}")

                return {
                    'status': 'success',
                    'message': 'State and date updated successfully for ticket.approval and related ticket.job.order',
                }

            # Update ticket.job.order directly if no ticket.approval found
            ticket_job_order = request.env['ticket.job.order'].sudo().browse(ticket_id)
            if ticket_job_order.exists():
                ticket_job_order.write(update_data)
                _logger.info(f"Updated ticket.job.order ID {ticket_id} with state {new_state} and date {new_date}")
                return {
                    'status': 'success',
                    'message': 'State and date updated successfully for ticket.job.order',
                }

            # If neither record exists, return an error
            return {'status': 'error', 'message': 'Ticket not found in either class'}

        except Exception as e:
            _logger.error(f"Error updating state and date: {str(e)}")
            return {'status': 'error', 'message': f"Exception: {str(e)}"}


    @http.route('/api/tickets/get', type='json', auth='user', methods=['POST'], csrf=False)
    def get_tickets(self):
        """Fetch tickets for the logged-in user's unit and display member names in `assignees_name`."""

        # Step 1: Get the current user's ID
        current_user_id = request.env.user.id

        # Step 2: Find the unit_name of the current user in osoul.tickets.team.member
        team_member = request.env['osoul.tickets.team.member'].sudo().search([('member_name', '=', current_user_id)], limit=1)

        # Check if the user has a unit assigned
        if not team_member or not team_member.unit_name:
            return {'status': 'error', 'message': 'User has no unit assigned.'}

        # Step 3: Use unit_name to filter tickets
        unit_name = team_member.unit_name
        domain = [('responsible_unit', '=', unit_name)]

        # Step 4: Search for tickets matching the domain
        tickets = request.env['ticket.approval'].sudo().search(domain)

        # Step 5: Prepare the result with the assignee names from osoul.tickets.team.member
        result = []
        for ticket in tickets:
            # Fetch `assignees_name` directly from the ticket
            assignees = ticket.assignees_name.mapped('member_name.name')  # Retrieves names of assigned technicians
            assignee_names = ', '.join(assignees)

            # Append ticket data with assignees_name field
            ticket_data = ticket.read([
                'job_order_sequence', 'responsible_unit', 'state', 'priority', 'description','ticket_date','employee_id','requester_no','department','location',
                'solution','issue_location_id','approval_date','under_progress_date','hold_date','finish_date','time_to_start','time_difference',
            ])[0]
            ticket_data['assignees_name'] = assignee_names  # Add assignees_name with team members

            result.append(ticket_data)

        # Step 6: Return the filtered tickets
        return {'status': 'success', 'tickets': result}


        # Step 6: Return the filtered tickets
        return {'status': 'success', 'tickets': result}


    @http.route('/api/session/info', type='json', auth='user', methods=['GET'], csrf=False)
    def get_session_info(self):
        """Get session information for the logged-in user."""
        user = request.env.user

        # Fetch the user's unit from the osoul.tickets.team.member model
        team_member = request.env['osoul.tickets.team.member'].sudo().search([('member_name', '=', user.id)], limit=1)

        user_info = {
            'user_id': user.id,
            'login': user.login,
            'name': user.name,
            'email': user.email,
            'responsible_unit': team_member.unit_name if team_member else 'N/A',
        }
        return {'status': 'success', 'user_info': user_info}


    @http.route('/api/tickets/debug', type='json', auth='user', methods=['GET'], csrf=False)
    def debug_fields(self):
        fields = request.env['ticket.approval']._fields.keys()
        return {'status': 'success', 'fields': list(fields)}
