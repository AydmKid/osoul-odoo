from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date


class StudentRegistrationForm(models.Model):
    _name = 'student.registration.form'
    _description = 'Student Registration Form'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "student_name"

    # Basic Student Information
    student_name = fields.Char(string="Student Name", required=True, tracking=True)
    student_identity_no = fields.Char(string="Identity No", required=True, tracking=True)
    circle_id = fields.Many2one('student.circles', string='Circle')
    stage_id = fields.Many2one('quran.stage', string="Stage")
    # Nationality selection from predefined list
    nationality = fields.Selection(
        string="Nationality",
        selection=[
            ('saudi', 'Saudi Arabia'),
            ('egypt', 'Egypt'),
            ('usa', 'United States'),
            ('uk', 'United Kingdom'),
            ('uae', 'United Arab Emirates'),
            ('canada', 'Canada'),
            ('india', 'India'),
            ('pakistan', 'Pakistan'),
            ('yemen', 'Yemen'),
            ('jordan', 'Jordan'),
            ('syria', 'Syria'),
            ('lebanon', 'Lebanon'),
            ('kuwait', 'Kuwait'),
            ('qatar', 'Qatar'),
            ('bahrain', 'Bahrain'),
            ('oman', 'Oman'),
            ('sudan', 'Sudan'),
            ('morocco', 'Morocco'),
            ('algeria', 'Algeria'),
            ('tunisia', 'Tunisia'),
            ('other', 'Other')
        ],
        tracking=True
    )

    date_of_birth = fields.Date(string="Date of Birth", tracking=True)
    age = fields.Integer(string="Age", compute="_compute_age", store=True, tracking=True)
    residence_location = fields.Char(string="Residence Location", tracking=True)
    parent_mobile = fields.Char(string="Parent's Mobile Number", tracking=True)
    other_mobile = fields.Char(string="Other Mobile Number", tracking=True)
    academic_level = fields.Char(string="Academic Level", tracking=True)

    teacher_id = fields.Many2one('school.teacher', string="Assigned Teacher")
    
    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for rec in self:
            if rec.date_of_birth:
                born = rec.date_of_birth
                rec.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                rec.age = 0

    def open_student_hearing_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Student Hearing Details'),
            'res_model': 'student.schedule.line',
            'view_mode': 'tree',
            'domain': [
                ('student_id', '=', self.id),
                ('is_present', '=', True)  
            ],
            'target': 'current',
        }
    def open_student_stage_tested_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Student Stage Test'),
            'res_model': 'student.stage.transition.test',
            'view_mode': 'tree',
            'domain': [
                ('student_id', '=', self.id),
                ('state', '!=', 'draft'),
            ],
            'target': 'current',
        }

    def open_student_review_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Student Review Details'),
            'res_model': 'student.review.line',
            'view_mode': 'tree',
            'domain': [
                ('student_id', '=', self.id),
                ('is_review', '=', True) 
            ],
            'target': 'current',
        }


    @api.constrains('student_identity_no', 'parent_mobile', 'other_mobile')
    def _check_phone_and_identity_no(self):
        for record in self:
            if not record.student_identity_no.isdigit() or len(record.student_identity_no) != 10:
                raise ValidationError(_("Identity No must be exactly 10 digits and contain only numbers."))

            identity_exists = self.search_count([
                ('student_identity_no', '=', record.student_identity_no),
                ('id', '!=', record.id)
            ])
            if identity_exists:
                raise ValidationError(_("Identity No already exists!"))

            def validate_mobile(value, label):
                if value and (not value.isdigit() or len(value) != 10):
                    raise ValidationError(_("%s must be exactly 10 digits and contain only numbers.") % label)

            validate_mobile(record.parent_mobile, "Parent's Mobile Number")
            validate_mobile(record.other_mobile, "Other Mobile Number")

            if record.parent_mobile:
                exists = self.search_count([
                    ('parent_mobile', '=', record.parent_mobile),
                    ('id', '!=', record.id)
                ])
                if exists:
                    raise ValidationError(_("Parents' mobile number already exists!"))

            if record.other_mobile:
                exists = self.search_count([
                    ('other_mobile', '=', record.other_mobile),
                    ('id', '!=', record.id)
                ])
                if exists:
                    raise ValidationError(_("Other Mobile Number already exists!"))

                    
    @api.constrains('circle_id')
    def _check_circle_capacity(self):
        for record in self:
            if record.circle_id:
                student_count = self.search_count([('circle_id', '=', record.circle_id.id)])
                if student_count > record.circle_id.max_students:
                    raise ValidationError(
                        _("The circle '%s' is full and cannot accept more than %s students.")
                        % (record.circle_id.name, record.circle_id.max_students)
                    )

