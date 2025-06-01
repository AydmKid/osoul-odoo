from odoo.exceptions import ValidationError
from odoo import models, fields, api, _

class OsoulBuffetStock(models.Model):
    _name = 'osoul.buffet.stock'
    _description = 'Buffet Stock'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Stock Name", required=True, tracking=True, unique=True)
    subcategory_id = fields.Many2one(comodel_name="osoul.buffet.subcategory", string="Subcategory", tracking=True, required=True, ondelete='cascade')
    quantity = fields.Integer(string="Quantity", tracking=True, default=0, readonly=True)
    description = fields.Text(string="Description", tracking=True)
    low_stock_threshold = fields.Integer(string="Low Stock Threshold", default=10, help="Minimum quantity before stock is considered low.", tracking=True)
    state = fields.Selection([('in_stock', 'In Stock'), ('low_stock', 'Low Stock'), ('out_of_stock', 'Out of Stock')], string="Stock State", compute="_compute_stock_state", store=True, tracking=True)

    @api.depends('quantity', 'low_stock_threshold')
    def _compute_stock_state(self):
        for record in self:
            if record.quantity <= 0:
                record.state = 'out_of_stock'
            elif record.quantity <= record.low_stock_threshold:
                record.state = 'low_stock'
            else:
                record.state = 'in_stock'

    _sql_constraints = [
        ('unique_stock_name', 'unique(name)', 'The stock name must be unique.'),
    ]

    def action_add_quantity(self):
        """ Open a wizard to add more stock quantity """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Stock Quantity',
            'res_model': 'buffet.stock.add.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_stock_id': self.id,
            }
        }


class BuffetStockMovement(models.Model):
    _name = 'buffet.stock.movement'
    _description = 'Buffet Stock Movement'
    _rec_name = 'stock_id'

    stock_id = fields.Many2one('osoul.buffet.stock', string="Stock Item", required=True)
    quantity_change = fields.Integer(string="Quantity Added", required=True)
    movement_date = fields.Datetime(string="Date", default=fields.Datetime.now, readonly=True)
    reason = fields.Char(string="Reason", required=True)
    user_id = fields.Many2one('res.users', string="Responsible User", default=lambda self: self.env.user, readonly=True)