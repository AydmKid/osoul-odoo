from odoo import api, fields, models

class OsoulOccuMember(models.Model):
    _name = "osoul.occu.member"
    _description = "Osoul Occupation Member"
    _rec_name = "member_name_id"

    member_name_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Member Name",
        domain=lambda self: self._get_member_domain()
    )

    employement_no = fields.Char(related='member_name_id.employment_no', string="Id", tracking=True)
    phone_no = fields.Char(string="Phone No", tracking=True)
    department = fields.Many2one(related='member_name_id.department_id', string="Department", tracking=True, store=True)
    image_1920 = fields.Image(related='member_name_id.image_1920', string="Profile Picture", store=True, readonly=False)

    @api.model
    def _get_member_domain(self):
        # Get all used employee IDs from existing records
        used_ids = self.env['osoul.occu.member'].search([]).mapped('member_name_id.id')
        return [('id', 'not in', used_ids)]

    # Optional SQL constraint for database-level enforcement
    _sql_constraints = [
        ('member_unique', 'UNIQUE(member_name_id)',
         'This employee is already added as a member!'),
    ]