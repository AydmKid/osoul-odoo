from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import date

class OsoulWaterContract(models.Model):
    _name = 'osoul.water.contract'
    _description = 'Water Contract'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Contract Name", required=True, tracking=True)
    sequence = fields.Char(string="Contract No", copy=False, readonly=True, default=lambda self: self.env['ir.sequence'].next_by_code('osoul.water.contract'))
    first_party = fields.Selection([
        ('acc', 'Arabian Cooperative Company'),
        ('caapp', 'Assir Poultry')], string="First Party", tracking=True, required=True)

    second_party = fields.Many2one(comodel_name="osoul.water.vendor", string="Second Party", tracking=True, required=True, ondelete="restrict")
    contract_start = fields.Date(string="Contract Start", required=True)
    contract_ends = fields.Date(string="Contract End", required=True)
    remaining_days = fields.Integer(string="Remaining Days", compute="_compute_remaining_days", store=True)
    document = fields.Binary(string="Contract Document", tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('expired', 'Expired')], string="State", default='draft', tracking=True)

    _sql_constraints = [
        ('contract_name_unique', 'UNIQUE(name)', 'The contract name must be unique')]

    @api.depends('contract_ends')
    def _compute_remaining_days(self):
        for record in self:
            if record.contract_ends:
                today = date.today()
                record.remaining_days = (record.contract_ends - today).days
            else:
                record.remaining_days = 0

    @api.constrains('contract_start', 'contract_ends')
    def _check_contract_dates(self):
        for record in self:
            if record.contract_start and record.contract_ends and record.contract_start > record.contract_ends:
                raise ValidationError("Contract End Date must be after the Contract Start Date!")