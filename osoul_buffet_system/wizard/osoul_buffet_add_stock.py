from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class BuffetStockAddWizard(models.TransientModel):
    _name = 'buffet.stock.add.wizard'
    _description = 'Add Stock Wizard'

    stock_id = fields.Many2one('osoul.buffet.stock', string="Stock Item", required=True)
    quantity_to_add = fields.Integer(string="Quantity to Add", required=True)
    reason = fields.Char(string="Reason for Stock Addition", required=True)

    def add_quantity(self):
        """ Add quantity to stock and record in stock movement """
        for wizard in self:
            if wizard.quantity_to_add <= 0:
                raise ValidationError(_("The quantity to add must be greater than zero."))

            stock = wizard.stock_id
            stock.quantity += wizard.quantity_to_add

            # Record the stock movement
            self.env['buffet.stock.movement'].create({
                'stock_id': stock.id,
                'quantity_change': wizard.quantity_to_add,
                'reason': wizard.reason,
                'user_id': self.env.user.id,
            })