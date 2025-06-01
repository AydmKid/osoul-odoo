from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Circles(models.Model):
    _name = 'student.circles'
    _description = 'Student Circles'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'sequence, name'

    # Basic Info
    name = fields.Char(string='Circle Name', required=True, tracking=True)
    code = fields.Char(string='Circle Code', tracking=True)
    description = fields.Text(string='Description', tracking=True)
    circle_type = fields.Selection([
        ('al-Qaida_al-nooraniya', 'Al-Qaida Al-Nooraniya'),
        ('general_session', 'General Session'),
    ], string="Circle Type", store=True, tracking=True)

    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(default=True, tracking=True)

    # Teacher & Students
    teacher_id = fields.Many2one(
        'school.teacher', string='Teacher',
        tracking=True, ondelete='set null'
    )
    max_students = fields.Integer(string='Maximum Students', default=20, tracking=True)
    student_ids = fields.One2many('student.registration.form', 'circle_id', string='Students')
    student_count = fields.Integer(
        compute='_compute_student_count', string='Number of Students', store=True
    )

    # Mail Thread Fields
    message_main_attachment_id = fields.Many2one(
        'ir.attachment', string="Main Attachment",
        domain="[('res_model', '=', _name), ('res_id', '=', id)]",
        copy=False
    )
    message_follower_ids = fields.One2many('mail.followers', 'res_id', string='Followers')
    activity_ids = fields.One2many('mail.activity', 'res_id', string='Activities')
    message_ids = fields.One2many('mail.message', 'res_id', string='Messages')

    # Compute student count
    @api.depends('student_ids')
    def _compute_student_count(self):
        for record in self:
            record.student_count = len(record.student_ids)

    # Validate student count limit
    @api.constrains('max_students', 'student_ids')
    def _check_max_students(self):
        for record in self:
            if record.student_count > record.max_students:
                raise ValidationError(_('The number of students cannot exceed the maximum allowed students.'))

    # Custom display name
    def name_get(self):
        result = []
        for record in self:
            name = f"[{record.code}] {record.name}" if record.code else record.name
            result.append((record.id, name))
        return result

    # Toggle archive status
    def toggle_active(self):
        for record in self:
            record.active = not record.active

    # Override unlink to archive students instead of deleting
    def unlink(self):
        for record in self:
            record.student_ids.write({'active': False})
        return super(Circles, self).unlink()

    # Clean up teacher references
    @api.model
    def _fix_teacher_constraints(self):
        circles = self.search([('teacher_id', '!=', False)])
        for circle in circles:
            if not circle.teacher_id.exists():
                circle.write({'teacher_id': False})
