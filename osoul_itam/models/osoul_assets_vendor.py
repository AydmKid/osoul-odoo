from odoo import api, fields, models, _

class OsoulItamAssetVendor(models.Model):
    _name = 'osoul.itam.assets.vendor'
    _description = 'Osoul Asset Vendor'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Vendor Name', required=True, tracking=True, help="The official name of the vendor or supplier.")
    company_name = fields.Char(string='Company Name', help="Legal name of the vendor’s company (if different from Vendor Name).")
    vendor_code = fields.Char(string='Vendor Code', help="Unique internal code or reference for this vendor.")
    phone = fields.Char(string='Phone', help="Primary contact phone number for the vendor.")
    email = fields.Char(string='Email', help="Primary contact email address for the vendor.")
    website = fields.Char(string='Website', help="Vendor's official website URL.")
    street = fields.Char(string='Street', help="Street name and number of the vendor’s address.")
    street2 = fields.Char(string='Street 2', help="Additional address information.")
    city = fields.Char(string='City', help="City in which the vendor is located.")
    state_id = fields.Many2one('res.country.state', string='State', help="State or province of the vendor’s address.")
    country_id = fields.Many2one('res.country', string='Country', help="Country of the vendor.")
    zip = fields.Char(string='ZIP', help="ZIP or postal code of the vendor’s address.")
    notes = fields.Text(string='Notes', help="Additional internal notes or remarks about the vendor.")
    active = fields.Boolean(string='Active', default=True, help="Toggle whether the vendor is currently active and selectable.")

    # Optionally, if you want to link back to assets or show how many assets a vendor provides:

    @api.model
    def create(self, vals):
        # Add custom logic on vendor creation if required.
        return super(OsoulItamAssetVendor, self).create(vals)