from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class OsoulOccuDailyCheckup(models.Model):
    _name = 'osoul.occu.daily.checkup'
    _description = 'Daily checkup for occupational health'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    sequence = fields.Char(string="Checkup No", readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one(comodel_name="res.users", string="Performed By", default=lambda self: self.env.user, readonly=True)
    date = fields.Datetime(string="Date and Time", default=fields.Datetime.now, readonly=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    location_id = fields.Many2many(comodel_name="osoul.occu.location", string="Location", tracking=True)
    # PUMP CLASS.
    #============
    line_pump_ids = fields.One2many(comodel_name="osoul.occu.pump.line", inverse_name='checkup_id', string="Pumps Line")
    total_pumps = fields.Integer(string='Total Pumps', compute="_compute_total_pumps", store=True)
    checked_pumps = fields.Integer(string="Checked Pumps", compute="_compute_checked_pumps", store=True)
    # FIRE PANEL CLASS.
    #==================
    line_fap_ids = fields.One2many(comodel_name="osoul.occu.fap.line", inverse_name="checkup_id", string="FAP's Lines")
    total_panels = fields.Integer(string="Total Panels", compute="_compute_total_panels", store=True)
    checked_panels = fields.Integer(string="Checked Panels", compute="_compute_checked_panels", store=True)
    # TANK CLASS.
    #============
    line_tank_ids = fields.One2many(comodel_name="osoul.occu.tank.line", inverse_name="checkup_id", string="Tanks Line")
    total_tanks = fields.Integer(string="Total Tanks", compute="_compute_total_tanks", store=True)
    checked_tanks = fields.Integer(string="Checked Tanks", compute="_compute_checked_tanks", store=True)
    completion_percentage = fields.Float(string="Completion Percentage", compute="_compute_completion_percentage", store=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('close', 'Close')], default="draft", readonly=True)

    # COMPUTE COMPLETION PERCENTAGE
    #========================================================================================================================
    @api.depends('checked_pumps', 'total_pumps', 'checked_panels', 'total_panels', 'checked_tanks', 'total_tanks')
    def _compute_completion_percentage(self):
        for record in self:
            total_items = record.total_pumps + record.total_panels + record.total_tanks
            checked_items = record.checked_pumps + record.checked_panels + record.checked_tanks

            record.completion_percentage = (checked_items / total_items * 100) if total_items else 0

    #========================================================================================================================
    # PUMPS SECTION.
    #========================================================================================================================
    @api.depends('line_pump_ids')
    def _compute_total_pumps(self):
        for record in self:
            record.total_pumps = len (record.line_pump_ids)

    # CHECKED PUMPS COUNTER.
    #==================================
    @api.depends('line_pump_ids.state')
    def _compute_checked_pumps(self):
        for record in self:
            record.checked_pumps = len(record.line_pump_ids.filtered(lambda pump: pump.state == "checked"))

    #========================================================================================================================
    # FIRE ALARM PANEL SECTION.
    #========================================================================================================================
    # INSERTED PANEL's COUNTER.
    #========================
    @api.depends('line_fap_ids')
    def _compute_total_panels(self):
        for record in self:
            record.total_panels = len (record.line_fap_ids)

    # CHECKED PANELS COUNTER.
    #==================================
    @api.depends('line_fap_ids.state')
    def _compute_checked_panels(self):
        for record in self:
            record.checked_panels = len(record.line_fap_ids.filtered(lambda panel: panel.state == "checked"))

    #========================================================================================================================
    # TANK's SECTION.
    #========================================================================================================================
    # INSERTED TANK's COUNTER.
    #========================
    @api.depends('line_tank_ids')
    def _compute_total_tanks(self):
        for record in self:
            record.total_tanks = len (record.line_tank_ids)

    # CHECKED TANK's COUNTER.
    #==================================
    @api.depends('line_tank_ids.state')
    def _compute_checked_tanks(self):
        for record in self:
            record.checked_tanks = len(record.line_tank_ids.filtered(lambda tank: tank.state == "checked"))

    #========================================================================================================================
    # BUTTON TO OPEN CHECKUP.
    #========================================================================================================================
    def action_open_checkup(self):
        for record in self:
            # Ensure Site and Location are set
            if not record.site_id or not record.location_id:
                raise ValidationError(_("Please set both the Site and Location before starting the checkup."))
            # Fetch related records
            pumps = self.env['osoul.occu.pump'].search([('site_id', '=', record.site_id.id),
                                                        ('location_id', '=', record.location_id.ids), ('state', '=', 'ready')])
            panels = self.env['osoul.occu.fap'].search([('site_id', '=', record.site_id.id),
                                                        ('location_id', '=', record.location_id.ids), ('state', '=', 'ready')])
            tanks = self.env['osoul.occu.tank'].search([('site_id', '=', record.site_id.id),
                                                        ('location_id', '=', record.location_id.ids), ('state', '=', 'ready')])
            pump_lines = [(0, 0, {'pump_id': pump.id}) for pump in pumps]
            panel_lines = [(0, 0, {'panel_id': panel.id}) for panel in panels]
            tank_lines = [(0, 0, {'tank_id': tank.id}) for tank in tanks]
            # Change Selected Pumps State
            pumps.state = "under_check"
            panels.state = "under_check"
            tanks.state = "under_check"
            # Update record with found items
            record.update({
                'line_pump_ids': pump_lines,
                'line_fap_ids': panel_lines,
                'line_tank_ids': tank_lines,})
            record.sequence = self.env['ir.sequence'].next_by_code('osoul.occu.checkup') or _('New')
            record.state = "open"
    
    def action_close_checkup(self):
        for record in self:
            pumps = self.env['osoul.occu.pump'].search([('site_id', '=', record.site_id.id),
                                                        ('location_id', '=', record.location_id.ids), ('state', '=', 'under_check')])
            panels = self.env['osoul.occu.fap'].search([('site_id', '=', record.site_id.id),
                                                        ('location_id', '=', record.location_id.ids), ('state', '=', 'under_check')])
            tanks = self.env['osoul.occu.tank'].search([('site_id', '=', record.site_id.id),
                                                        ('location_id', '=', record.location_id.ids), ('state', '=', 'under_check')])
            
            pumps.state = "ready"
            panels.state = "ready"
            tanks.state = "ready"
            record.state = "close"
        return

    def buttonClick(self):
        raise ValidationError(_("Button Clicked !"))