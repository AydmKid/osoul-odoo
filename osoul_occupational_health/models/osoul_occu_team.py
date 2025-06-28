from odoo import _, api, fields, models, tools

class OsoulOccuTeam(models.Model):
    _name = 'osoul.occu.team'
    _description = 'Occupational Health Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'
    _rec_name = 'name'

     # Basic Information
    name = fields.Char(string='Name', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    photo = fields.Image(string="Photo")
    notes = fields.Text(string="Notes")

    # Contact & Identification
    mobile = fields.Char(string="Mobile Number")
    email = fields.Char(string="Email")
    date_of_birth = fields.Date(string="Date of Birth")
    hire_date = fields.Date(string="Hire Date")
    address = fields.Char(string="Address")

    # Relations
    user_id = fields.Many2one(
    'res.users',
    string="Related User",
    # default=lambda self: self.env.user,
    tracking=True
    )

    # Toggle archive/active status
    def toggle_active(self):
        for record in self:
            record.active = not record.active