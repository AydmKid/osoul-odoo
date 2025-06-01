from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

class OsoulBuffetCategory(models.Model):
    _name = 'osoul.buffet.category'
    _description = 'Buffet Category'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Category Name", required=True, tracking=True, unique=True)
    subcategory_ids = fields.One2many('osoul.buffet.subcategory', 'category_id', string="Subcategories", tracking=True)
    description = fields.Text(string="Description", tracking=True)

    _sql_constraints = [
        ('unique_category_name', 'unique(name)', 'The category name must be unique.'),
    ]




class OsoulBuffetSubcategory(models.Model):
    _name = 'osoul.buffet.subcategory'
    _description = 'Buffet Subcategory'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(string="Subcategory Name", required=True, tracking=True, unique=True)
    category_id = fields.Many2one(comodel_name="osoul.buffet.category", string="Category", tracking=True, required=True, ondelete='cascade')
    stock_ids = fields.One2many('osoul.buffet.stock', 'subcategory_id', string="Stocks", tracking=True)
    description = fields.Text(string="Description", tracking=True)

    _sql_constraints = [
        ('unique_subcategory_name', 'unique(name)', 'The subcategory name must be unique.'),
    ]