from odoo import _, api, fields, models, tools

class OsoulItamAssetsSoftware(models.Model):
    _name = 'osoul.itam.assets.software'
    _description = ''
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    

    # Assets Software Information's
    name = fields.Char(string='Software Name', required=True, tracking=True)
    license_key = fields.Char(string='License Key', help="The software license key or activation code.")
    license_type = fields.Selection([('named_user', 'Named User'),
                                     ('concurrent', 'Concurrent'),
                                     ('subscription', 'Subscription')], string='License Type', help="Type of software license: Named User, Concurrent, or Subscription.")
    license_count = fields.Integer(string='License Count', help="Number of licenses purchased or allocated for this software.")
    version = fields.Char(string='Version', help="Software version or firmware release.")
    brand = fields.Many2one('osoul.itam.assets.brand', string='brand', required=True, tracking=True)
    vendor_id = fields.Many2one('osoul.itam.assets.vendor', string='Vendor Name', tracking=True)
    vendor_contract_start = fields.Datetime(string='', required=True)
    vendor_contract_end = fields.Date(string='Vendor Contract End', help="Date when the vendor support or contract ends.")
    purchase_price = fields.Float(string='Purchase Price', tracking=True)