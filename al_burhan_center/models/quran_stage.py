from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class QuranStage(models.Model):
    _name = 'quran.stage'
    _description = 'Quran Memorization Stage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char(string='Stage Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)
    description = fields.Text(string="Description")
    surah_ids = fields.One2many('quran.surah', 'stage_id', string="Surahs in this Stage")
    surah_count = fields.Integer(string="Surah Count", compute="_compute_surah_count", store=True)

    @api.depends('surah_ids')
    def _compute_surah_count(self):
        for record in self:
            record.surah_count = len(record.surah_ids)
