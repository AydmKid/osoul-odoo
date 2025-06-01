from odoo import _, api, fields, models

class OsoulItamAssetsCategory(models.Model):
    _name = 'osoul.itam.assets.category'
    _description = 'Asset Categories for ITAM System'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    _sql_constraints = [
        ('unique_category_name', 'unique(name)', 
         'The category name must be unique. Please choose a different name.')]

    name = fields.Char(string='Name', required=True, tracking=True, help="Name of the asset category.")
    total_sub_category = fields.Integer(string="S.Categories", compute="_compute_sub_categories")
    sub_category_ids = fields.One2many('osoul.itam.assets.sub.category', 'category_id', string='Subcategories')

    @api.depends('sub_category_ids')
    def _compute_sub_categories(self):
        # Optimized using read_group for performance
        subcategories_grouped = self.env['osoul.itam.assets.sub.category'].read_group([('category_id', 'in', self.ids)], 
            ['category_id'], 
            ['category_id'])
        counts = {data['category_id'][0]: data['category_id_count'] for data in subcategories_grouped}
        for record in self:
            record.total_sub_category = counts.get(record.id, 0)



from odoo import _, api, fields, models

class OsoulItamAssetsSubCategory(models.Model):
    _name = 'osoul.itam.assets.sub.category'
    _description = 'Subcategories for Asset Categories in ITAM System'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    _sql_constraints = [
        ('unique_sub_category', 'unique(name)', 
         'The subcategory name must be unique. Please choose a different name.')]

    name = fields.Char(string='Sub Category', required=True, tracking=True, help="Name of the asset subcategory.")
    category_id = fields.Many2one('osoul.itam.assets.category', string='Category', required=True, tracking=True,
                                  help="The category to which this subcategory belongs.")
