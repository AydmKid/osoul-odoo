from odoo import models, fields, api, _


class SchoolTeacher(models.Model):
    _name = 'school.teacher'
    _description = 'School Teacher'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    # Basic Information
    name = fields.Char(string='Name', required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    photo = fields.Image(string="Photo")
    notes = fields.Text(string="Notes")

    # Contact & Identification
    identification_number = fields.Char(string="ID Number")
    mobile = fields.Char(string="Mobile Number")
    email = fields.Char(string="Email")
    date_of_birth = fields.Date(string="Date of Birth")
    hire_date = fields.Date(string="Hire Date")
    address = fields.Char(string="Address")

    # Relations
    user_id = fields.Many2one(
    'res.users',
    string="Related User",
    default=lambda self: self.env.user,
    tracking=True
    )


    # Circles the teacher is assigned to
    circle_ids = fields.One2many('student.circles', 'teacher_id', string='Circles')
    circle_count = fields.Integer(
        compute='_compute_circle_count',
        string='Number of Circles',
        store=True
    )

    # Students supervised by the teacher
    student_ids = fields.One2many(
        'student.registration.form', 'teacher_id', string="Students"
    )

    # Compute number of circles
    @api.depends('circle_ids')
    def _compute_circle_count(self):
        for record in self:
            record.circle_count = len(record.circle_ids)

    # Toggle archive/active status
    def toggle_active(self):
        for record in self:
            record.active = not record.active

    # Override delete: archive students and circles first
    def unlink(self):
        for record in self:
            # Archive related students
            record.student_ids.write({'active': False})
            # Archive related circles
            record.circle_ids.write({'active': False})
        return super(SchoolTeacher, self).unlink()

    @api.model
    def create(self, vals):
        if not vals.get('user_id') and self.env.uid:
            vals['user_id'] = self.env.uid
        return super(SchoolTeacher, self).create(vals)

    _sql_constraints = [
    ('unique_user_id', 'unique(user_id)', 'This user is already assigned to a teacher.'),
    ]

