from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError

class LegalAffairsPromissoryNote(models.Model):
    _name = "legal.affairs.promissory.note"
    _description = ""
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "enfoncer_against_id"

    note_date = fields.Date(string="Note Date", tracking=True)
    note_no = fields.Char(string="Note No", tracking=True)
    used_currency_id = fields.Many2one('res.currency', string="Used Currency", ondelete='restrict', tracking=True)
    note_value = fields.Float(string="Note Value", tracking=True)
    enfoncer_id = fields.Many2one(comodel_name='res.partner', string="Enfoncer", ondelete='restrict', tracking=True)
    enfoncer_mobile = fields.Char(string="Enfoncer Mobile", related='enfoncer_id.mobile', tracking=True) 
    enfoncer_against_id = fields.Many2one(comodel_name='res.partner', string="Enfoncer Against", ondelete='restrict', tracking=True)
    enfoncer_against_mobile = fields.Char(string="Enfoncer Against Mobile", related='enfoncer_against_id.mobile', tracking=True)
    due_type = fields.Selection([('on_date','On Date'),('on_order','On Order'),], string="Due Type", default="on_date", tracking=True)
    due_date = fields.Date(string="Due Date", tracking=True)
    due_days_left = fields.Integer(string="Due Days Left", compute="_compute_due_days_left", tracking=True)
    note_creation_location = fields.Many2one(comodel_name="countries.cities", string="Creation Location", tracking=True)
    due_location = fields.Many2one(comodel_name="countries.cities", string="Due Location", tracking=True)
    guarantor_id = fields.Many2one(comodel_name='res.partner', string="Guarantor", ondelete='restrict', tracking=True)
    guarantor_mobile = fields.Char(string="Guarantor Mobile", related='guarantor_id.mobile', tracking=True)
    promissory_note_copy = fields.Binary(string="Copy of Promissory Note")
    legal_affairs_authorized_id = fields.Many2one(comodel_name='res.users', string="Legal Affairs Authorized", ondelete='restrict', readonly=True, tracking=True)
    legal_affairs_approval = fields.Selection([('waiting_approval','Waiting for Approval'),('approved','Approved')], string="Approval", readonly=True, tracking=True)
    state = fields.Selection([('draft','Draft'),('waiting_approval','Waiting for Approval'),('running','Running'),
                              ('paid','Paid'),('cancel','Cancelled'),], default="draft", readonly=True, string="Promissory Note Satae", tracking=True)

    @api.depends('due_date')
    def _compute_due_days_left(self):
        for record in self:
            if record.due_date:
                today = fields.Date.today()
                days_left = record.due_date - today
                record. due_days_left = days_left.days
            else:
                record.due_days_left = 0

    def action_button_waiting_approval(self):
        for rec in self:
            rec.state = "waiting_approval"
            rec.legal_affairs_approval = "waiting_approval"
    
    def action_button_approval(self):
        self.legal_affairs_authorized_id = self.env.user.id
        self.legal_affairs_approval = "approved"
        self.state = "running"

    def action_button_paid(self):
        self.state = "paid"

    def action_button_late(self):
        self.state = "late"

    def action_button_cancel(self):
        self.state = "cancel"

    def unlink(self):
        for note in self:
            deletable_state = ['draft']
            if note.state and note.state not in deletable_state:
                raise ValidationError(_("Promissory Note cannot be deleted anymore. Please contact the system administrator."))
            else:
                return super().unlink()