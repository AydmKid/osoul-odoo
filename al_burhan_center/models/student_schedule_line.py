from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentScheduleLine(models.Model):
    _name = 'student.schedule.line'
    _description = 'Student Schedule Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "schedule_id"
    _order = 'create_date desc'

    # Link to memorization schedule
    schedule_id = fields.Many2one(
        'student.memorization.schedule',
        string="Circle Name",
        required=True,
        ondelete='cascade'
    )

    # Student info
    student_id = fields.Many2one(
        'student.registration.form',
        string="Student",
        required=True
    )
    stage_id = fields.Many2one(
        'quran.stage',
        string="Stage",
        related="student_id.stage_id",
        store=True,
        readonly=False
    )
    student_identity_no_id = fields.Char(
        string="Student Identity No",
        related="student_id.student_identity_no",
        readonly=True,
        store=True,
        tracking=True
    )

    # Teacher info (fetched from schedule)
    teacher_id = fields.Many2one(
        'school.teacher',
        string="Teacher",
        related="schedule_id.teacher_id",
        store=True,
        readonly=True
    )

    # Memorization range
    start_surah_id = fields.Many2one(
        'quran.surah',
        string="Start Surah",
        domain="[('stage_id', '=', stage_id)]",
        tracking=True
    )
    start_ayah_number = fields.Integer(string="Start Ayah", tracking=True)

    end_surah_id = fields.Many2one(
        'quran.surah',
        string="End Surah",
        domain="[('stage_id', '=', stage_id)]",
        tracking=True
    )
    end_ayah_number = fields.Integer(string="End Ayah", tracking=True)

    # Recitation info
    recited_pages = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ], string="Recited Pages", store=True, tracking=True)

    is_recited = fields.Boolean(string="Recited", store=True, default=False,readonly=True,tracking=True)
    is_present = fields.Boolean(string="Present", default=False, tracking=True)

    @api.model_create_single
    def create(self, vals):
        if vals.get('teacher_comments'):
            vals['is_recited'] = True
        return super().create(vals)



    def write(self, vals):
        if 'teacher_comments' in vals:
            vals['is_recited'] = bool(vals['teacher_comments'])
        return super().write(vals)


    # Auto Recited
    @api.onchange('teacher_comments')
    def _onchange_teacher_comments(self):
        for rec in self:
            rec.is_recited = bool(rec.teacher_comments)

    # Auto Present
    @api.onchange('is_recited')
    def _onchange_is_recited(self):
        for rec in self:
            if rec.is_recited:
                rec.is_present = True

    # Evaluation for memorization
    teacher_comments = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('weak', 'Weak')
    ], string="Teacher Evaluation", store=True, tracking=True)

    # Additional optional review evaluation (not used unless needed)
    teacher_comments_review = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('weak', 'Weak')
    ], string="Evaluation Review", store=True, tracking=True)

    # Related state from schedule
    state = fields.Selection(
        related="schedule_id.state",
        string="Status",
        store=True,
        tracking=True
    )

    # Prevent duplicate student in same schedule
    @api.constrains('schedule_id', 'student_id')
    def _check_student_unique_in_schedule(self):
        for rec in self:
            if rec.schedule_id:
                students = rec.schedule_id.line_ids.filtered(
                    lambda l: l.student_id == rec.student_id and l.id != rec.id
                )
                if students:
                    raise ValidationError(
                        _("Student '%s' is already added to the same schedule.") % rec.student_id.display_name
                    )

    # stop enter aya bigger thant total of ayayt on the sora
    @api.constrains('start_surah_id', 'start_ayah_number', 'end_surah_id', 'end_ayah_number')
    def _check_ayah_within_surah(self):
        for rec in self:
            if rec.start_surah_id and rec.start_ayah_number:
                if rec.start_ayah_number > rec.start_surah_id.ayah_count:
                    raise ValidationError(
                        _("Start Ayah (%s) exceeds total ayahs in '%s' (%s).") %
                        (rec.start_ayah_number, rec.start_surah_id.name, rec.start_surah_id.ayah_count)
                    )

            if rec.end_surah_id and rec.end_ayah_number:
                if rec.end_ayah_number > rec.end_surah_id.ayah_count:
                    raise ValidationError(
                        _("End Ayah (%s) exceeds total ayahs in '%s' (%s).") %
                        (rec.end_ayah_number, rec.end_surah_id.name, rec.end_surah_id.ayah_count)
                    )
