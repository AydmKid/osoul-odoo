from datetime import datetime
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OsoulOccuWorkPermit(models.Model):
    _name = 'osoul.occu.work.permit'
    _description = 'Occupational Work Permit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Permit Name", tracking=True)
    permit_no = fields.Char(string="Permit No", readonly=True)
    permit_site = fields.Many2one('osoul.occu.site', string="Permit Site")
    permit_location = fields.Many2one('osoul.occu.location', string="Permit Location", domain="[('site_id', '=', permit_site)]")
    permit_for = fields.Many2one(comodel_name="hr.department", string="Permit For")
    description = fields.Text(string="Work Description")
    valid_from = fields.Datetime(string="Valid From")
    valid_to = fields.Datetime(string="Valid To")
    permit_duration = fields.Char(string="Permit Duration", compute="_compute_permit_duration", store=True)
    work_type = fields.Many2many(comodel_name="osoul.occu.work.type", string="Work Type")
    hazard_risk = fields.Many2many(comodel_name="osoul.occu.hazard", string="Hazards & Risks")
    action_taken = fields.Many2many(comodel_name="osoul.occu.actions", string="Action Taken")
    protective_equips = fields.Many2many(comodel_name="osoul.occu.personal.protective", string="Protective Equipments")
    checkup_ids = fields.One2many('osoul.occu.checkup', 'permit_id', string="Checkup")
    work_executor = fields.Many2one(comodel_name="hr.employee", string="Work Executor")
    executor_signature = fields.Binary(string="Executor Signature")
    agreement_date = fields.Date(string="Agreement Date", readonly=True)
    permit_image = fields.Binary("Permit Image", attachment=True)
    work_agreement = fields.Text(string="Work Approval", readonly=True, default="""I have read and understand the above conditions and precautions.
I accept responsibility for carrying out the work as specified.
I will ensure the men under my control read, understand and comply with these conditions and precautions.
I will notify the Area Authority on completion or suspension of this work.
(If an accident occurs or work is stopped due to non-compliance by workers or contractors with the safety department's procedures,
the safety department and the company are exempted from its responsibility)
If the contractor wants to complete the suspended work, a new permit must be obtained.""")
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'),
                              ('approved', 'Approved'), ('rejected', 'Rejected'),
                              ('closed', 'Closed')], default='draft', string="Status", tracking=True)
    # permit_image = fields.Binary("Permit Image", attachment=True)
    
    @api.model
    def create(self, vals):
        if not vals.get('permit_no'):
            vals['permit_no'] = self.env['ir.sequence'].next_by_code('osoul.occu.work.permit') or _('New')
        record = super(OsoulOccuWorkPermit, self).create(vals)
        default_checkups = [
            {"check": "Has the site been inspected prior to starting work?"},
            {"check": "Is a valid operating license required for this activity?"},
            {"check": "Have flammable materials been cleared from the area?"},
            {"check": "Are safety barriers required to secure the area?"},
            {"check": "Has the equipment been inspected within the last year?"},
            {"check": "Are warning signs displayed in the work area?"},
            {"check": "Are weather conditions suitable for the work?"},
            {"check": "Is the temperature appropriate for safe operation?"},
        ]
        for checkup in default_checkups:
            self.env['osoul.occu.checkup'].create({'check': checkup['check'], 'permit_id': record.id})
        return record

    @api.depends('valid_from', 'valid_to')
    def _compute_permit_duration(self):
        for record in self:
            if record.valid_from and record.valid_to and record.valid_to > record.valid_from:
                duration = record.valid_to - record.valid_from
                days = duration.days
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, _seconds = divmod(remainder, 60)
                record.permit_duration = f"{days}d {hours}h {minutes}m"
            else:
                record.permit_duration = False

    @api.constrains('valid_from', 'valid_to')
    def _check_dates(self):
        for record in self:
            if not record.valid_from or not record.valid_to:
                raise ValidationError(_("Both 'Valid From' and 'Valid To' dates must be provided."))
            if record.valid_from >= record.valid_to:
                raise ValidationError(_("The 'Valid To' date must be later than the 'Valid From' date."))

    def action_submit(self):
        for record in self:
            record.state = 'submitted'
            record.message_post(body=_("Work Permit has been submitted for approval."))

    def action_approve(self):
        for record in self:
            record.state = 'approved'
            record.message_post(body=_("Work Permit has been approved."))

    def action_reject(self):
        for record in self:
            record.state = 'rejected'
            record.message_post(body=_("Work Permit has been rejected."))

    def action_close(self):
        for record in self:
            record.state = 'closed'
            record.message_post(body=_("Work Permit has been closed."))




from odoo import fields, models, api

class OsoulOccuCheckup(models.Model):
    _name = 'osoul.occu.checkup'
    _description = 'Work Permit Quiz'

    permit_no = fields.Char(string="Permit No", related='permit_id.permit_no', store=True)
    check = fields.Char(string="Check", required=True)
    answer = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Answer", required=True, default='no')
    permit_id = fields.Many2one(comodel_name='osoul.occu.work.permit', string="Work Permit", ondelete='cascade')

    @api.model
    def unlink(self):
            # Block programmatic deletion of records
            raise ValidationError(_("You cannot delete checkups."))
