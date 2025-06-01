from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError

class LegalAffairsCourtSession(models.Model):
    _name = "legal.affairs.court.session"
    _description = "Next Court Session"
    _rec_name = "session_subject"
    
    court_session_id = fields.Many2one(comodel_name='legal.affairs.court.case', string='Court Session', tracking=True)
    la_employee_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user.id, readonly=True, tracking=True)
    case_no_id = fields.Char(related="court_session_id.case_no", readonly=True, tracking=True)
    session_date = fields.Date(string="Session Date", tracking=True)
    session_reminder_date = fields.Date(string="Reminder Date", tracking=True)
    session_type = fields.Selection([('online', 'Online'), ('present', 'Present')], string="Session Type", tracking=True)
    session_subject = fields.Char(string="Session Subject", tracking=True)
    session_details = fields.Text(string="Session Details", tracking=True)
    session_state = fields.Selection([
        ('open', 'Open'),
        ('closed', 'Closed')
    ], string="Session State", default="open", readonly=True, tracking=True)

    @api.onchange('session_date', 'session_reminder_date')
    def _check_session_reminder_date_validation(self):
        for rec in self:
            if rec.session_reminder_date and rec.session_date and rec.session_reminder_date > rec.session_date:
                raise ValidationError(_("Reminder date cannot be after the session date."))

    @api.depends('session_reminder_date')
    def _check_session_reminder_date(self):
        for record in self:
            today = fields.Date.today()
            if today == record.session_reminder_date:
                message = {
                    'type':'ir.actions.client',
                    'tag':'display_notification',
                    'params':{
                        'title': ('warning'),
                        'message':'Next Session Reminder',
                        'stucky':True
                    }
                }
                return message
                
    def action_close_open_session(self):
        for rec in self:
            if not rec.session_details:
                raise ValidationError(_("Please enter session short details before closing the session"))
            else:
                rec.session_state = "closed"
    
    def unlink(self):
        for rec in self:
            if rec.session_state == "closed":
                raise UserError(_("Cannot delete a closed court session."))
        return super(LegalAffairsCourtSession, self).unlink()