from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StudentReviewLine(models.Model):
    _name = 'student.review.line'
    _description = 'Student Review Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "schedule_review_id"
    _order = 'create_date desc'

    # Link to memorization schedule (review type)
    schedule_review_id = fields.Many2one(
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

    # Teacher info (read-only, comes from schedule)
    teacher_id = fields.Many2one(
        'school.teacher',
        string="Teacher",
        related="schedule_review_id.teacher_id",
        store=True,
        readonly=True
    )

    # Review details
    recited_pages = fields.Selection([
        ('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')
    ], string="Recited Pages", store=True, tracking=True)

    start_surah_review_id = fields.Many2one(
        'quran.surah',
        string="Review Start Surah",
        domain="[('stage_id', '=', stage_id)]",
        tracking=True
    )
    start_ayah_review_number = fields.Integer(string="Review Start Ayah", tracking=True)

    end_surah_review_id = fields.Many2one(
        'quran.surah',
        string="Review End Surah",
        domain="[('stage_id', '=', stage_id)]",
        tracking=True
    )
    end_ayah_review_number = fields.Integer(string="Review End Ayah", tracking=True)

    # Attendance
    is_review = fields.Boolean(string="Review", default=False)
    is_present = fields.Boolean(string="Present", default=False, tracking=True)

    @api.model_create_single
    def create(self, vals):
        if vals.get('teacher_comments_review'):
            vals['is_review'] = True
        return super().create(vals)



    def write(self, vals):
        if 'teacher_comments_review' in vals:
            vals['is_review'] = bool(vals['teacher_comments_review'])
        return super().write(vals)


    # Auto Recited
    @api.onchange('teacher_comments_review')
    def _onchange_teacher_comments(self):
        for rec in self:
            rec.is_review = bool(rec.teacher_comments_review)

    # Auto Present
    @api.onchange('is_review')
    def _onchange_is_review(self):
        for rec in self:
            if rec.is_review:
                rec.is_present = True

    # Evaluation
    teacher_comments_review = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('weak', 'Weak')
    ], string="Evaluation Review", store=True, tracking=True)

    # State from schedule
    state = fields.Selection(
        related="schedule_review_id.state",
        string="Status",
        store=True,
        tracking=True
    )

    # Prevent duplicate student entries in same review schedule
    @api.constrains('schedule_review_id', 'student_id')
    def _check_student_unique_in_schedule(self):
        for rec in self:
            if rec.schedule_review_id:
                students = rec.schedule_review_id.line_review_ids.filtered(
                    lambda l: l.student_id == rec.student_id and l.id != rec.id
                )
                if students:
                    raise ValidationError(_("Student '%s' is already added to the same review schedule.") % rec.student_id.display_name)
    
    # stop enter aya bigger thant total of ayayt on the sora
    @api.constrains('start_surah_review_id','start_ayah_review_number','end_surah_review_id','end_ayah_review_number')
    def _check_review_ayah_within_surah(self):
        for rec in self:
            if rec.start_surah_review_id and rec.start_ayah_review_number:
                if rec.start_ayah_review_number > rec.start_surah_review_id.ayah_count:
                    raise ValidationError(
                        _("Start Ayah (%s) exceeds total ayahs in '%s' (%s).") %
                        (rec.start_ayah_review_number, rec.start_surah_review_id.name, rec.start_surah_review_id.ayah_count)
                    )
            if rec.end_surah_review_id and rec.end_ayah_review_number:
                if rec.end_ayah_review_number > rec.end_surah_review_id.ayah_count:
                    raise ValidationError(
                        _("End Ayah (%s) exceeds total ayahs in '%s' (%s).") %
                        (rec.end_ayah_review_number, rec.end_surah_review_id.name, rec.end_surah_review_id.ayah_count)
                    )
