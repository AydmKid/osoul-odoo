from os import name
from odoo import _, api, fields, models, tools

class LegalAffairsPartner(models.Model):
    _inherit = "res.partner"

    contract_counter = fields.Integer(string="Contract Counter", compute="_computer_total_contracts")
    
    def _computer_total_contracts(self):
        for record in self:
            contracts = self.env['osoul.legal.affairs.contract'].search_count([('second_party_id.id', '=', record.id)])
            record.contract_counter = contracts