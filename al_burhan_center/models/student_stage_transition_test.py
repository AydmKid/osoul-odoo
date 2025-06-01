# Python Model: student_stage_transition_test.py
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class StudentStageTransitionTest(models.Model):
    _name = 'student.stage.transition.test'
    _description = 'Stage Transition Test'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'student_id'
    

    student_id = fields.Many2one('student.registration.form', string="Student", required=True, tracking=True)
    current_stage_id = fields.Many2one('quran.stage', string="Current Stage", tracking=True, store=True, readonly=True)
    target_stage_id = fields.Many2one('quran.stage', string="Target Stage", required=True, tracking=True)

    test_date = fields.Datetime(string="Test Date", default=fields.Datetime.now, tracking=True)
    teacher_id = fields.Many2one('school.teacher', string="Teacher", required=True, tracking=True)

    start_surah_id = fields.Many2one('quran.surah', string="Start Surah", domain="[('stage_id', '=', current_stage_id)]")
    end_surah_id = fields.Many2one('quran.surah', string="End Surah", domain="[('stage_id', '=', current_stage_id)]")

    # Scoring selections
    def _selection_1_10(self):
        return [('0', '0')] + [(str(i), str(i)) for i in range(1, 11)]

    def _selection_1_15(self):
        return [('0', '0')] + [(str(i), str(i)) for i in range(1, 16)]

    def _selection_1_5(self):
        return [('0', '0')] + [(str(i), str(i)) for i in range(1, 6)]


    # Questions 1 to 8
    question1 = fields.Selection(_selection_1_10, string="Question 1", default='0')
    question2 = fields.Selection(_selection_1_10, string="Question 2", default='0')
    question3 = fields.Selection(_selection_1_10, string="Question 3", default='0')
    question4 = fields.Selection(_selection_1_10, string="Question 4", default='0')
    question5 = fields.Selection(_selection_1_10, string="Question 5", default='0')
    question6 = fields.Selection(_selection_1_10, string="Question 6", default='0')
    question7 = fields.Selection(_selection_1_10, string="Question 7", default='0')
    question8 = fields.Selection(_selection_1_10, string="Question 8", default='0')

    # Tajweed and performance
    tajweed_score = fields.Selection(_selection_1_15, string="Tajweed", default='0')
    performance_score = fields.Selection(_selection_1_5, string="Performance", default='0')

    total_score = fields.Integer(string="Total Score", compute="_compute_total_score", store=True)

    is_passed = fields.Boolean(string="Passed", compute="_compute_is_passed", store=True)
    day_name = fields.Char(string="Day Name", compute="_compute_day_name", store=True)
    total_score_display = fields.Char(string="Score", compute="_compute_total_score_display", store=False)

    @api.depends('total_score')
    def _compute_total_score_display(self):
        for rec in self:
            rec.total_score_display = f"{rec.total_score}%" if rec.total_score else "0%"


    @api.depends('test_date')
    def _compute_day_name(self):
        for rec in self:
            rec.day_name = rec.test_date.strftime('%A') if rec.test_date else False

    state = fields.Selection([
        ('draft', 'Draft'),
        ('tested', 'Tested'),
        ('promoted', 'Promoted'),
        ('failed', 'Failed'),
    ], string="Status", default='draft', tracking=True)

    @api.onchange('student_id')
    def _onchange_student_id(self):
        for rec in self:
            if rec.student_id:
                rec.current_stage_id = rec.student_id.stage_id.id
                rec.teacher_id = rec.student_id.teacher_id.id

                # جلب السور حسب المرحلية
                surahs = self.env['quran.surah'].search([('stage_id', '=', rec.current_stage_id.id)], order='surah_number')
                if surahs:
                    rec.start_surah_id = surahs[0].id
                    rec.end_surah_id = surahs[-1].id


    @api.depends('total_score')
    def _compute_is_passed(self):
        for rec in self:
            rec.is_passed = rec.total_score >= 70

    @api.depends(
        'question1', 'question2', 'question3', 'question4',
        'question5', 'question6', 'question7', 'question8',
        'tajweed_score', 'performance_score'
    )
    def _compute_total_score(self):
        for rec in self:
            try:
                rec.total_score = sum([
                    int(rec.question1 or 0),
                    int(rec.question2 or 0),
                    int(rec.question3 or 0),
                    int(rec.question4 or 0),
                    int(rec.question5 or 0),
                    int(rec.question6 or 0),
                    int(rec.question7 or 0),
                    int(rec.question8 or 0),
                    int(rec.tajweed_score or 0),
                    int(rec.performance_score or 0),
                ])
            except ValueError:
                rec.total_score = 0

    def action_tested(self):
        self.state = 'tested'

    def action_promote(self):
        if not self.is_passed:
            raise ValidationError(_("The student must pass the test to be promoted."))
        self.state = 'promoted'
        self.student_id.stage_id = self.target_stage_id

    def action_fail(self):
        self.state = 'failed'

    @api.model_create_single
    def create(self, vals):
        if vals.get('student_id') and not vals.get('current_stage_id'):
            student = self.env['student.registration.form'].browse(vals['student_id'])
            vals['current_stage_id'] = student.stage_id.id
        return super().create(vals)

    def write(self, vals):
        if 'student_id' in vals and not vals.get('current_stage_id'):
            student = self.env['student.registration.form'].browse(vals['student_id'])
            vals['current_stage_id'] = student.stage_id.id
        return super().write(vals)