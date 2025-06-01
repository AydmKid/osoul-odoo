from odoo import _, api, fields, models, tools

class OsoulTicktesTeamMember(models.Model):
    _name ="osoul.tickets.team.member"
    _description = ""
    _rec_name = "member_name"

    unit_name = fields.Selection([
        ('networks', 'Networks'),
        ('systems', 'Systems'),
        ('technical_support', 'Technical Support'),
        ('developers', 'Developers'),
        ('operation', 'Operation'),
        ('information_technology_office', 'Information Technology Office')
    ], string='Unit Name')
    member_name = fields.Many2one(
        'res.users',
        string='Member Name',
        required=True,
        domain="[('groups_id.name', '=', 'Ticket Assignee')]"
    )
    color = fields.Integer(string="Color")

    