from odoo import _, api, fields, models

class OsoulBuffetOperator(models.Model):
    _name = 'osoul.buffet.operator'
    _description = 'Buffet Operator'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'

    name = fields.Many2one(comodel_name="hr.employee", string="Operator", tracking=True, required=True)
    phone = fields.Char(string="Phone No", related='name.mobile_phone', readonly=True)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    @api.depends('name')
    def _compute_display_name(self):
        for record in self:
            if record.name:
                record.display_name = f"{record.name.name} (Operator)"
            else:
                record.display_name = _("No Operator Selected")
