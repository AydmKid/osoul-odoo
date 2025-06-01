from odoo import _, api, fields, models, tools

class OsoulItamAssetsHardwareModel(models.Model):
    _name = "osoul.itam.assets.hardware.model"
    _description = "Hardware Models for ITAM System"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    _sql_constraints = [
        ('unique_model_name', 'unique(name)', 
         'The hardware model name must be unique. Please choose a different name.')]

    name = fields.Char(string="Model Name", required=True, tracking=True, help="Name of the hardware model.")
    brand_id = fields.Many2one(comodel_name='osoul.itam.assets.brand', string='brand',
                                      required=True, tracking=True, help="The brand of this hardware model.")
    category_id = fields.Many2one(comodel_name='osoul.itam.assets.category', string='Category', 
                                  required=True, tracking=True, help="The category to which this hardware model belongs.")
    sub_category_id = fields.Many2one(comodel_name="osoul.itam.assets.sub.category", string="Sub Category",
                                      required=True, help="The subcategory to which this hardware model belongs.")

    @api.onchange('category_id')
    def _onchange_category_id(self):
        """Filter subcategories based on the selected category."""
        if self.category_id:
            return {
                'domain': {'sub_category_id': [('category_id', '=', self.category_id.id)]}}
        return {'domain': {'sub_category_id': []}}
