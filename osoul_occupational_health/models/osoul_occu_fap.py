from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class OsoulOccuFAP(models.Model):
    _name = 'osoul.occu.fap'
    _description = 'Occupational Air Alarm Panel'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(string="Panel No", readonly=True, default=lambda self: _('New'))
    name = fields.Char(string="Panel Name", tracking=True, required=True)
    nfc_code = fields.Char(string="NFC Code", tracking=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    location_id = fields.Many2one(comodel_name="osoul.occu.location", string="Location", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.occu.fap') or _('New')
        return super(OsoulOccuFAP, self).create(vals)

#========================================================================================================================================#

#========================================================================================================================================#
class OsoulOccuFAPCheckupLine(models.Model):
    _name = 'osoul.occu.fap.line'
    _description = 'FAP Checkup Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    checkup_sequence = fields.Char(string="Checkup No", related='checkup_id.sequence')
    panel_id = fields.Many2one(comodel_name="osoul.occu.fap", string="Panel Name", required=True)
    sequence = fields.Char(string="Panel No", related='panel_id.sequence', readonly=True)
    nfc_code = fields.Char(string="NFC Code", related='panel_id.nfc_code', readonly=True)
    site_id = fields.Many2one(string="Site", related='panel_id.site_id', readonly=True)
    location_id = fields.Many2one(string="Location", related='panel_id.location_id', readonly=True)
    fire = fields.Integer(string="Fire Counter", tracking=True)
    troubles = fields.Integer(string="Troubles Counter", tracking=True)
    note = fields.Text(string="Note", tracking=True)
    state = fields.Selection([('checked', 'Checked'), ('not_checked', 'Not Checked')], default="not_checked", tracking=True)
    checkup_id = fields.Many2one(comodel_name="osoul.occu.fap.checkup", string="Checkup Reference", required=True)

    def action_scan_nfc(self):
        for record in self:
            if record.nfc_code:
                # Perform NFC validation logic (you may need an actual scanning system integration)
                record.state = 'checked'
                record.message_post(body=_("NFC Code scanned successfully. Panel checked."))
            else:
                raise UserError(_("No NFC code available for this panel."))
#========================================================================================================================================#

#========================================================================================================================================#
class OsoulOccuFAPCheckup(models.Model):
    _name = 'osoul.occu.fap.checkup'
    _description = 'FAP Checkup'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    sequence = fields.Char(string="Check No", readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one(comodel_name="res.users", string="Performed By", default=lambda self: self.env.user, readonly=True)
    date = fields.Datetime(string="Date and Time", default=fields.Datetime.now, readonly=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    line_ids = fields.One2many(comodel_name="osoul.occu.fap.line", inverse_name="checkup_id", string="Checkup Lines")
    total_panels = fields.Integer(string="Total Panels", readonly=True, compute="_compute_total_panels", store=True)
    checked_panels = fields.Integer(string="Checked Panels", readonly=True, compute="_compute_checked_panels", store=True)
    completion_percentage = fields.Float(string="Completion Percentage", readonly=True, compute="_compute_completion_percentage", store=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('close', 'Close')], default="draft", readonly=True)

    @api.depends('line_ids')
    def _compute_total_panels(self):
        for record in self:
            record.total_panels = len(record.line_ids)

    @api.depends('line_ids.state')
    def _compute_checked_panels(self):
        for record in self:
            record.checked_panels = sum(1 for line in record.line_ids if line.state == "checked")

    @api.depends('total_panels', 'checked_panels')
    def _compute_completion_percentage(self):
        for record in self:
            if record.total_panels > 0:
                record.completion_percentage = (record.checked_panels / record.total_panels) * 100
            else:
                record.completion_percentage = 0.0

    #==================================#
    """ BUTTONS FUNCTION """
    #==================================#
    def action_open(self):
        for record in self:
            record.state = "open"
            if not record.site_id:
                raise ValueError(_("Please select a site before loading panels."))

            # Clear existing lines
            record.line_ids = [(5, 0, 0)]

            # Fetch related fire panels
            fire_panels = self.env['osoul.occu.fap'].search([('site_id', '=', record.site_id.id)])

            if not fire_panels:
                raise ValidationError(_("No fire panels found for the selected site."))

            # Assign panels to line_ids
            record.line_ids = [(0, 0, {
                'panel_id': panel.id,
                'state': 'not_checked',
            }) for panel in fire_panels]

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.occu.fap.checkup') or _('New')
        return super(OsoulOccuFAPCheckup, self).create(vals)