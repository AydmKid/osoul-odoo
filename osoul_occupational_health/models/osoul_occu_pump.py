from odoo import _, api, fields, models, tools

class OsoulOccuPump(models.Model):
    _name = 'osoul.occu.pump'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence'

    sequence = fields.Char(string="Pump No", readonly=True, default=lambda self: _('New'))
    nfc_code = fields.Char(string="NFC Code", tracking=True)
    site_id = fields.Many2one(comodel_name="osoul.occu.site", string="Site", tracking=True)
    location_id = fields.Many2one(comodel_name="osoul.occu.location", string="Location", tracking=True)

    @api.model
    def create(self, vals):
        if vals.get('sequence', _('New')) == _('New'):
            vals['sequence'] = self.env['ir.sequence'].next_by_code('osoul.occu.pump') or _('New')
        return super(OsoulOccuPump, self).create(vals)