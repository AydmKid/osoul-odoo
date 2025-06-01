from odoo import models, fields, api, _
from datetime import datetime

class StudentMemorizationSchedule(models.Model):
    _name = 'student.memorization.schedule'
    _description = 'Student Memorization Schedule'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'circle_id'

    teacher_id = fields.Many2one(
        'school.teacher', string="Teacher",
        tracking=True,
        default=lambda self: self.env['school.teacher'].search([('user_id', '=', self.env.uid)], limit=1).id
    )

    sequence = fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default='New'
    )

    circle_id = fields.Many2one('student.circles', string="Circle", tracking=True)

    line_ids = fields.One2many('student.schedule.line', 'schedule_id', string="All Students")
    line_review_ids = fields.One2many('student.review.line', 'schedule_review_id', string="All Students")

    
    day_of_week = fields.Selection([
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ], string="Day of Week", required=True, tracking=True, default='sunday')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string="Status", default='draft', tracking=True)

    date_assigned = fields.Datetime(
        string="Date",
        default=fields.Datetime.now,
        readonly=True,
        tracking=True
    )

    day_name = fields.Char(string="Day Name", compute="_compute_day_name", store=True)

    lesson = fields.Text(string="Lesson Description", tracking=True)
    review = fields.Text(string="Review Notes", tracking=True)

    teacher_comments = fields.Selection([
        ('excellent', 'Excellent'),
        ('very_good', 'Very Good'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('weak', 'Weak')
    ], string="Teacher Evaluation", tracking=True)

    is_completed = fields.Boolean(string="Completed", compute="_compute_is_completed", store=True, tracking=True)
    student_count = fields.Integer(string="Total Students", compute="_compute_counts", store=True)
    review_student_count = fields.Integer(
    string="Total Review Students",
    compute="_compute_counts",
    store=True
    )
    stage_count = fields.Integer(
    string="Number of Stages",
    compute="_compute_counts",
    store=True
    )

    @api.depends('line_ids', 'line_review_ids')
    def _compute_counts(self):
        for rec in self:
            rec.student_count = len(rec.line_ids)
            rec.review_student_count = len(rec.line_review_ids)

            # Count unique stages from memorization students
            stages = rec.line_ids.mapped('student_id.stage_id')
            rec.stage_count = len(set(stages.ids))


    @api.depends('date_assigned')
    def _compute_day_name(self):
        for rec in self:
            rec.day_name = rec.date_assigned.strftime('%A') if rec.date_assigned else False

    @api.depends('teacher_comments')
    def _compute_is_completed(self):
        for rec in self:
            rec.is_completed = bool(rec.teacher_comments)

    @api.onchange('circle_id')
    def _onchange_circle_id(self):
        if self.circle_id:
            self.teacher_id = self.circle_id.teacher_id.id

            self.line_ids = [(5, 0, 0)]
            self.line_review_ids = [(5, 0, 0)]

            self.line_ids = [
                (0, 0, {
                    'student_id': student.id
                }) for student in self.circle_id.student_ids if student.id
            ]

            self.line_review_ids = [
                (0, 0, {
                    'student_id': student.id
                }) for student in self.circle_id.student_ids if student.id
            ]


    @api.model
    def create(self, vals):
        if vals.get('circle_id') and not vals.get('teacher_id'):
            circle = self.env['student.circles'].browse(vals['circle_id'])
            if circle.teacher_id:
                vals['teacher_id'] = circle.teacher_id.id

        if vals.get('sequence', 'New') == 'New':
            vals['sequence'] = self.env['ir.sequence'].next_by_code('student.memorization.schedule') or '/'

        return super().create(vals)

    def write(self, vals):
        if vals.get('circle_id') and not vals.get('teacher_id'):
            circle = self.env['student.circles'].browse(vals['circle_id'])
            if circle.teacher_id:
                vals['teacher_id'] = circle.teacher_id.id
        return super().write(vals)