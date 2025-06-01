from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class LegalAffairsContract(models.Model):
    _name = "osoul.legal.affairs.contract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = ""
    _rec_name = "record_no"

    record_no = fields.Char(string="Record No", readonly=True, tracking=True)
    contract_no = fields.Char(string="Contract No", tracking=True)
    contract_subject = fields.Char(string="Contract Subject", tracking=True)
    contract_signing_date = fields.Date(string="Singing Date", tracking=True)
    first_party = fields.Many2one(comodel_name='res.partner', string="First Party", ondelete='restrict', tracking=True)
    fp_representative_id = fields.Many2one(comodel_name='res.users', string="FP Representative", ondelete='restrict', tracking=True)
    second_party_id = fields.Many2one(comodel_name='res.partner', string="Second Party", ondelete='restrict', tracking=True)
    sp_representative_id = fields.Many2one(comodel_name='res.partner', string="SP Representative", ondelete='restrict', tracking=True)
    open_cantract = fields.Boolean(string="Open Contract", tracking=True)
    contract_start_date = fields.Date(string="Contracting Start Date", tracking=True)
    contract_end_date = fields.Date(string="Contract End Date", tracking=True)
    contract_end_alarm = fields.Date(string="End Contract Alarm", tracking=True)
    contract_duration = fields.Char(string="Contract Duration (Days)", compute="_compute_contract_duration", tracking=True)
    duration_to_end = fields.Char(string="Duration to End (Days)", compute="_compute_duration_to_end", tracking=True)
    # CONTRACT DETAILS
    contract_value = fields.Float(string="", tracking=True)
    contract_currency_id = fields.Many2one('res.currency', tracking=True)
    contract_terms = fields.Text(string="", tracking=True)
    payment_terms = fields.Text(string="Payment Terms", tracking=True)
    payment_method = fields.Selection([('cash','Cash'),('bank_transfare','Bank Transfare'),], tracking=True)
    contract_file = fields.Binary(string="Contract File", tracking=True)
    # AUTHORIZED USERS AND APPROVALS
    contract_responsable_authorized_id = fields.Many2one(comodel_name='res.users', string='Contract Responsable', ondelete='restrict', tracking=True)
    contract_responsable_approval = fields.Selection([('ready','Ready'),('waiting_for_approval', 'Waiting For Approval'),
                                                      ('approved','Approved')], string="Contract Responsable Approval", default="ready", tracking=True)
    legal_affairs_authorized_id = fields.Many2one('res.users', string="Legal Affairs Authorized", readonly=True, tracking=True)
    legal_affairs_approval = fields.Selection([('ready','Ready'),('waiting_for_approval', 'Waiting For Approval'),
                                               ('approved','Approved')], string="Legal Affairs Approval", default="ready", tracking=True)
    vice_president_authorized_id = fields.Many2one('res.users', string="Vice President Authorized", ondelete='restrict', readonly=True, tracking=True)
    vice_president_approval = fields.Selection([('ready','Ready'),('waiting_for_approval', 'Waiting For Approval'),
                                       ('approved','Approved')], string="Vice President Approval", default="ready", tracking=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('approvals', 'Approvals'),
                              ('running', 'Running'),
                              ('expire', 'Expired'),
                              ('cancel', 'Cancelled'),], string='Status', default='draft', tracking=True)
    contract_manual_end_date = fields.Date(string="Contract Ending Date", readonly=True, tracking=True)
    contract_cancel_date = fields.Date(string="Contract Cancel Date", readonly=True, tracking=True)

    # CONTRACT DATES CHECK
    @api.constrains('contract_start_date', 'contract_end_date')
    def _check_contract_dates(self):
        for record in self:
            if record.contract_start_date and record.contract_end_date:
                if record.contract_start_date > record.contract_end_date:
                    raise ValidationError(_("Contract start date cannot be greater than contract end date."))

    # CONTRACT END ALARM CHECK
    @api.constrains('contract_end_alarm', 'contract_end_date')
    def _check_contract_end_alarm_constrains(self):
        for record in self:
            if record.contract_end_alarm and record.contract_end_alarm:
                if record.contract_end_alarm > record.contract_end_date:
                    raise ValidationError(_("Contract end alarm date cannot be greater than contract end date."))

    # CONTRACT DURATION CHECK
    @api.depends('contract_end_date','contract_start_date')
    def _compute_contract_duration(self):
        for record in self:
            if record.contract_end_date and record.contract_start_date:
                if record.open_cantract == True:
                    period = record.contract_end_date - record.contract_start_date
                    record.contract_duration = period.days
            else:
                record.contract_duration = 0

    # CONTRACT DURATION TO END CALCULATIONS
    @api.depends('contract_end_date')
    def _compute_duration_to_end(self):
        for record in self:
            if record.contract_end_date:
                period = record.contract_end_date - fields.Date.today()
                record.duration_to_end = period.days
            else:
                record.duration_to_end = 0

    # NOTIFICATION OF CONTRACT END
    @api.depends('contract_end_alarm')
    def _check_contract_end_alarm(self):
        for record in self:
            today = fields.Date.today()
            if today == record.contract_end_alarm:
                message = {
                    'type':'ir.actions.client',
                    'tag':'display_notification',
                    'params':{
                        'title': ('warning'),
                        'message':'Contract About to End',
                        'stucky':True
                    }
                }
                return message

    # MAIN STATE BUTTONS AND RECORD SEQUENCE
    def action_button_approvals(self):
        for rec in self:
            rec.state = "approvals"
            rec.contract_responsable_approval = "waiting_for_approval"
            rec.legal_affairs_approval = "waiting_for_approval"
            rec.vice_president_approval = "waiting_for_approval"
            rec.record_no = self.env["ir.sequence"].next_by_code("legal_affairs_contract_sequence")
            
    # ALL APPROVALS CHECK
    def action_button_running(self):
        for rec in self:
            if rec.legal_affairs_approval and rec.contract_responsable_approval and rec.vice_president_approval:
                if rec.legal_affairs_approval and rec.contract_responsable_approval and rec.vice_president_approval != "approved":
                    raise ValidationError (_("Authrization Serise Not Completed to Make This Contract Running"))
                else:
                    rec.state = "running"


    # CONTACTS AUTHORIZED USERS APPROVALS 
    def action_contract_responsable_approval(self):
        for rec in self:
            if self.env.user.id != rec.contract_responsable_authorized_id.id:
                raise ValidationError(_("You are not autherised to approve this contract, contact system administrator"))
            else:
                rec.contract_responsable_approval = "approved"

    # LEGAL AFFAIRS APPROVAL BUTTON
    def action_legal_affairs_approval(self):
        for rec in self:
            rec.legal_affairs_authorized_id = self.env.user.id
            rec.legal_affairs_approval = "approved"

    # VICE PRESIDENT APPROVAL BUTTON
    def action_vice_president_approval(self):
        for rec in self:
            rec.vice_president_authorized_id = self.env.user.id
            rec.vice_president_approval = "approved"
            rec.state = "running"

    # CONTRACT AUTO OR MANUAL ENDS
    def action_button_end(self):
        for rec in self:
            rec.state = "expire"
            rec.contract_manual_end_date = fields.Date.today()

    # CONTRACT MANUAL CANCEL
    def action_button_cancel(self):
        for rec in self:
            rec.state = "cancel"
            rec.contract_cancel_date = fields.Date.today()

    def unlink(self):
        deletable_state = ['draft']
        for contract in self:
            if contract.state and contract.state not in deletable_state:
                raise ValidationError(_("Contract cannot be deleted anymore. Please contact the system administrator."))
        return super().unlink()