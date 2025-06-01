from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class LegalAffairsCourtCase(models.Model):
    _name = "legal.affairs.court.case"
    _description = ""
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "case_no"

    record_no = fields.Char(string="", tracking=True)
    la_employee_id = fields.Many2one(comodel_name='res.users',default=lambda self: self.env.user.id, readonly=True, tracking=True)
    case_no = fields.Char(string="", tracking=True)
    case_subject = fields.Char(string="Case Subject", tracking=True)
    case_open_date = fields.Date(string="Case Open Date", tracking=True)
    position_in_case = fields.Selection([('plaintiff','Plaintiff'),
                                 ('respondent','Respondent')], string="Position", tracking=True)
    plaintiff_name_id = fields.Many2one(comodel_name='res.partner', string="Plaintiff Name", tracking=True)
    respondent_name_id = fields.Many2one(comodel_name='res.partner', string="Respondent Name", tracking=True)
    session_ids = fields.One2many(comodel_name='legal.affairs.court.session', inverse_name='court_session_id', string='Next Court Sessions', tracking=True)
    open_sessions_counter = fields.Integer(string="Total Open Sessions in Case", compute="_compute_total_sessions", tracking=True)
    state = fields.Selection([('draft','Draft'),
                              ('open','Open'),
                              ('closed','Closed'),], default="draft", tracking=True)

    def _compute_total_sessions(self):
        for rec in self:
            counter = self.env['legal.affairs.court.session'].search_count([('court_session_id', '=', rec.id),('session_state','=','open')])
            rec.open_sessions_counter = counter

    def action_case_open(self):
        for rec in self:
            rec.record_no = self.env['ir.sequence'].next_by_code('legal_affairs_court_case_sequence')
            rec.state = "open"

    def action_case_close(self):
        for rec in self:
            if rec.open_sessions_counter != 0:
                raise ValidationError(_("All open sessions must be closed before closed the case."))
            else:
                rec.state = "closed"

    def action_open_sessions(self):
        return

    def unlink(self):
        for case in self:
            deletable_state = ['draft']
            if case.state and case.state not in deletable_state:
                raise ValidationError(_("Case cannot be deleted anymore. Please contact the system administrator."))
            else:
                return super().unlink()