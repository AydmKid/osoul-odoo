from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class QuranSurah(models.Model):
    _name = 'quran.surah'
    _description = 'Quran Surah'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'surah_number'

    name = fields.Char(string='Surah Name', required=True, tracking=True)
    surah_number = fields.Integer(string='Surah Number', required=True, tracking=True)
    ayah_count = fields.Integer(string='Number of Ayahs', required=True, tracking=True)
    place_of_revelation = fields.Selection(
        [
            ('meccan', 'Meccan'),
            ('medinan', 'Medinan'),
        ],
        string='Place of Revelation',
        required=True,
        tracking=True
    )
    start_ayah = fields.Integer(string="Start Ayah")
    end_ayah = fields.Integer(string="End Ayah")
    stage_id = fields.Many2one('quran.stage', string='Stage', tracking=True)

    _sql_constraints = [
        ('surah_number_unique', 'unique(surah_number)', 'Surah number must be unique!')
    ]

    @api.constrains('surah_number', 'ayah_count')
    def _check_positive_numbers(self):
        for record in self:
            if record.surah_number <= 0:
                raise ValidationError(_('Surah number must be a positive integer.'))
            if record.ayah_count <= 0:
                raise ValidationError(_('Number of Ayahs must be a positive integer.'))
