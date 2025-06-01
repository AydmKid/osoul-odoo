from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

#==========================================
    # FIRE ALARM PANEL CLASS.
#==========================================
class OsoulOccuFAP(models.Model):
    _name = 'osoul.occu.fap'
    _description = 'Occupational Fire Alarm Panels'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(string="Panel No", readonly=True, default=lambda self: _('New'))
    name = fields.Char(string="Panel Name", tracking=True, required=True)
    nfc_code = fields.Char(string="NFC Code", tracking=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    location_id = fields.Many2one(comodel_name="osoul.occu.location", string="Location", tracking=True)
    state = fields.Selection([('ready', 'Ready'), ('under_check', 'Under Check')], default="ready", readonly=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.occu.fap') or _('New')
        return super(OsoulOccuFAP, self).create(vals)

#=========================================
    # FIRE ALARM PANEL LINE.
#=========================================
class OsoulOccuFAPCheckupLine(models.Model):
    _name = 'osoul.occu.fap.line'
    _description = 'FAP Checkup Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    checkup_id = fields.Many2one(comodel_name="osoul.occu.daily.checkup", string="Checkup Reference", required=True)
    checkup_sequence = fields.Char(string="Checkup No", related='checkup_id.sequence')
    panel_id = fields.Many2one(comodel_name="osoul.occu.fap", string="Panel Name",
                               domain="[('state', '=', 'ready'), ('site_id', '=', parent.site_id), ('location_id', 'in', parent.location_id)]", readonly=True)
    sequence = fields.Char(string="Panel No", related='panel_id.sequence', store=True)
    nfc_code = fields.Char(string="NFC Code", related='panel_id.nfc_code', store=True, readonly=True)
    site_id = fields.Many2one(string="Site", related='panel_id.site_id', store=True)
    location_id = fields.Many2one(string="Location", related='panel_id.location_id')
    status = fields.Selection([('draft', 'Draft'), ('ok', 'OK'), ('not_ok', 'Not OK')], string="Status", readonly=True, default="draft")
    state = fields.Selection([('draft', 'Draft'), ('checked', 'Checked'), ('not_checked', 'Not Checked')], default="draft", tracking=True, readonly=True)

    fire = fields.Integer(string="Fire Counter", tracking=True)
    troubles = fields.Integer(string="Troubles Counter", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    def action_checked(self):
        for record in self:
            record.state = "checked"

    def action_status_ok(self):
        for record in self:
            record.status = "ok"

    def action_status_not_ok(self):
        for record in self:
            record.status = "not_ok"

#==========================================
    # PUMP CLASS.
#==========================================
class OsoulOccuPump(models.Model):
    _name = 'osoul.occu.pump'
    _description = 'Occupational Pumps'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(string="Pump No", readonly=True, default=lambda self: _('New'))
    name = fields.Char(string="Pump Name", tracking=True, required=True)
    nfc_code = fields.Char(string="NFC Code", tracking=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    location_id = fields.Many2one(comodel_name="osoul.occu.location", string="Location", tracking=True)
    state = fields.Selection([('ready', 'Ready'), ('under_check', 'Under Check')], default="ready", readonly=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.occu.pump') or _('New')
        return super(OsoulOccuPump, self).create(vals)
    
#==========================================
    # PUMPS LINE.
#==========================================
class OsoulOccuPumpLine(models.Model):
    _name = 'osoul.occu.pump.line'
    _description = 'Pumps Checkup Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    checkup_id = fields.Many2one(comodel_name="osoul.occu.daily.checkup", string="Checkup Reference")
    checkup_sequence = fields.Char(string="Checkup No", related='checkup_id.sequence')
    pump_id = fields.Many2one(comodel_name="osoul.occu.pump", string="Pump Name",
                              domain="[('state', '=', 'ready'), ('site_id', '=', parent.site_id), ('location_id', 'in', parent.location_id)]", readonly=True)
    sequence = fields.Char(string="Panel No", related='pump_id.sequence', store=True)
    nfc_code = fields.Char(string="NFC Code", related='pump_id.nfc_code', store=True, readonly=True)
    site_id = fields.Many2one(string="Site", related='pump_id.site_id', store=True)
    location_id = fields.Many2one(string="Location", related='pump_id.location_id', store=True, readonly=True)
    status = fields.Selection([('draft', 'Draft'), ('ok', 'OK'), ('not_ok', 'Not OK')], string="Status", default="draft", readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('checked', 'Checked'), ('not_checked', 'Not Checked')], default="draft", tracking=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    def action_checked(self):
        for record in self:
            record.state = "checked"

    def action_status_ok(self):
        for record in self:
            record.status = "ok"

    def action_status_not_ok(self):
        for record in self:
            record.status = "not_ok"

#==========================================
    # TANKS CLASS.
#==========================================
class OsoulOccuTank(models.Model):
    _name = 'osoul.occu.tank'
    _description = 'Occupational Tanks'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    sequence = fields.Char(string="Tank No", readonly=True, default=lambda self: _('New'))
    name = fields.Char(string="Tank Name", tracking=True, required=True)
    nfc_code = fields.Char(string="NFC Code", tracking=True)
    type = fields.Selection([('diesel_tank', 'Diesel Tank'), ('gasoline_tank', 'Gasoline Tank'),
                             ('water_tank', 'Water Tank')], string="Tank Type", tracking=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    location_id = fields.Many2one(comodel_name="osoul.occu.location", string="Location", tracking=True)
    state = fields.Selection([('ready', 'Ready'), ('under_check', 'Under Check')], default="ready", readonly=True, tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.occu.tank') or _('New')
        return super(OsoulOccuTank, self).create(vals)

#==========================================
    # TANK LINE.
#==========================================
class OsoulOccuTankLine(models.Model):
    _name = 'osoul.occu.tank.line'
    _description = 'Tanks Checkup Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    checkup_id = fields.Many2one(comodel_name="osoul.occu.daily.checkup", string="Checkup Reference")
    checkup_sequence = fields.Char(string="Checkup No", related='checkup_id.sequence')
    tank_id = fields.Many2one(comodel_name="osoul.occu.tank", string="Tank Name",
                              domain="[('state', '=', 'ready'), ('site_id', '=', parent.site_id), ('location_id', 'in', parent.location_id)]", readonly=True)
    sequence = fields.Char(string="Panel No", related='tank_id.sequence', store=True)
    nfc_code = fields.Char(string="NFC Code", related='tank_id.nfc_code', store=True, readonly=True)
    site_id = fields.Many2one(string="Site", related='tank_id.site_id', store=True)
    location_id = fields.Many2one(string="Location", related='tank_id.location_id', store=True)
    status = fields.Selection([('draft', 'Draft'), ('ok', 'OK'), ('not_ok', 'Not OK')], string="Status", readonly=True, default="draft")
    state = fields.Selection([('draft', 'Draft'), ('checked', 'Checked'), ('not_checked', 'Not Checked')], default="draft", tracking=True, readonly=True)
    remarks = fields.Text(string="Remarks", tracking=True)

    def action_checked(self):
        for record in self:
            record.state = "checked"

    def action_status_ok(self):
        for record in self:
            record.status = "ok"

    def action_status_not_ok(self):
        for record in self:
            record.status = "not_ok"