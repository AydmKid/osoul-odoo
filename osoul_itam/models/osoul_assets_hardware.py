from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import base64
import qrcode
from io import BytesIO

class OsoulItamAssetHardware(models.Model):
    _name = 'osoul.itam.assets.hardware'
    _description = 'Osoul Asset Hardware'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # General Asset Information
    name = fields.Char(string='Asset Name',  tracking=True)
    asset_tag = fields.Char(string='Asset Tag', readonly=True, index=True)
    category_id = fields.Many2one('osoul.itam.assets.category',  string='Category', tracking=True)
    sub_category_id = fields.Many2one('osoul.itam.assets.sub.category',  string='Sub Category', tracking=True)
    brand = fields.Many2one('osoul.itam.assets.brand', string='brand',  tracking=True)
    model_id = fields.Many2one(comodel_name="osoul.itam.assets.hardware.model", string="Model Name",  tracking=True)
    vendor_id = fields.Many2one('osoul.itam.assets.vendor', string='Vendor')
    serial_number = fields.Char(string='Serial Number',  tracking=True, index=True)
    qr_code = fields.Binary(string="QR Code", readonly=True, attachment=True, help="QR Code generated for the Serial Number.")
    site_name = fields.Selection([('assir_poultry', 'Assir Poultry'),
                                  ('operation_office','Operation Office'),
                                  ('jeddah_office','Jeddah Office'),
                                  ('hatchery','Hatchery')], string='Site',  tracking=True, default="assir_poultry")
    location = fields.Char(string='Location', tracking=True)
    purchase_date = fields.Date(string='Purchase Date')
    purchase_price = fields.Monetary(string='Purchase Price', currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.company.currency_id.id, tracking=True, readonly=True)
    warranty_number = fields.Char(string='Warranty Number', tracking=True)
    warranty_expiration = fields.Date(string='Warranty Expiration', tracking=True)
    days_until_warranty = fields.Integer(string='Warranty Days Left', compute='_compute_days_until_warranty', store=True)
    notes = fields.Text(string='Notes', tracking=True)

    # Depreciation Calculations
    salvage_value = fields.Monetary(string='Salvage Value', currency_field='currency_id', tracking=True)
    useful_life_years = fields.Integer(string='Useful Life (Years)', tracking=True)
    annual_depreciation_rate = fields.Float(string='Annual Depreciation', digits=(12, 2), compute='_compute_annual_depreciation_rate', store=True)
    
    state = fields.Selection([('in_stock', 'In Stock'), ('in_use', 'In Use'),
                              ('maintenance', 'In Maintenance'), ('retired', 'Retired'),
                              ('scrap','Scrap')], string='Lifecycle State', default='in_stock', tracking=True)
    
    # PC, Laptop, and Mobile Asset Information
    cpu = fields.Char(string='CPU', help="CPU model or type installed in the asset.")
    memory_type = fields.Selection([('ddr', 'DDR'), ('ddr2', 'DDR2'), ('ddr3', 'DDR3'), ('ddr4', 'DDR4'),
                                    ('ddr5', 'DDR5'), ('lpddr3', 'LPDDR3'), ('lpddr4', 'LPDDR4'), ('lpddr5', 'LPDDR5'),
                                    ('gddr5', 'GDDR5 (Graphics)'), ('gddr6', 'GDDR6 (Graphics)'),
                                    ('gddr6x', 'GDDR6X (Graphics)'), ('hbm', 'HBM (High Bandwidth Memory)'),
                                    ('hbm2', 'HBM2'), ('sram', 'SRAM'), ('dram', 'DRAM')], string="RAM Type", tracking=True)
    memory_gb = fields.Selection([('1_gb', ''), ('2_gb', ''),
                                  ('4_gb', ''), ('', ''),
                                  ('', ''), ('', ''),])
    storage_gb = fields.Float(string='Storage (GB)', tracking=True)
    mac_address = fields.Char(string='MAC Address', tracking=True)
    end_of_life_date = fields.Date(string='End of Life Date', tracking=True)

    # Unique Constraints
    _sql_constraints = [
        ('unique_serial_number', 'unique(serial_number)', 'The Serial Number must be unique!'),
        ('unique_name', 'unique(name)', 'Asset Name must be unique!')
    ]

    # Auto-generate Asset Tag
    @api.model
    def create(self, vals):
        if not vals.get('asset_tag'):
            seq = self.env['ir.sequence'].next_by_code('osoul.assets.hardware')
            vals['asset_tag'] = seq if seq else _('New')
        return super(OsoulItamAssetHardware, self).create(vals)

    # Calculate Annual Depreciation Rate
    @api.depends('purchase_price', 'salvage_value', 'useful_life_years')
    def _compute_annual_depreciation_rate(self):
        for asset in self:
            if asset.useful_life_years:
                depreciation_base = asset.purchase_price - asset.salvage_value
                asset.annual_depreciation_rate = depreciation_base / asset.useful_life_years
            else:
                asset.annual_depreciation_rate = 0.0

    # Calculate Days Until Warranty Expiration
    @api.depends('warranty_expiration')
    def _compute_days_until_warranty(self):
        today = fields.Date.today()
        for record in self:
            if record.warranty_expiration:
                days_left = (record.warranty_expiration - today).days
                record.days_until_warranty = max(days_left, 0)
            else:
                record.days_until_warranty = 0

    # Onchange for Category
    @api.onchange('category_id')
    def _onchange_category_id(self):
        if self.category_id:
            self.sub_category_id = False
            return { 
                'domain': {'sub_category_id': [('category_id', '=', self.category_id.id)]}
            }
        
    @api.onchange('brand')
    def _onchange_brand(self):
        if self.brand:
            self.model_id = False
            return {
                'domain': {'model_id': [('brand_id', '=', self.brand.id)]}
            }

    # Check Warranty Expiration Validation
    @api.constrains('warranty_expiration', 'purchase_date')
    def _check_warranty_expiration(self):
        for record in self:
            if record.warranty_expiration and record.purchase_date and record.warranty_expiration < record.purchase_date:
                raise ValidationError(_('Warranty expiration date (%s) cannot be before the purchase date (%s).') % 
                                      (record.warranty_expiration, record.purchase_date))

    # Scheduled Action to Update Asset State Based on End of Life Date
    @api.model
    def _check_end_of_life(self):
        today = fields.Date.today()
        expired_assets = self.search([('end_of_life_date', '<', today), ('state', '!=', 'retired')])
        for asset in expired_assets:
            asset.state = 'retired'

    # Scheduler to run daily
    def _scheduler_check_end_of_life(self):
        self._check_end_of_life()

    # Button Action to Generate QR Code
    def action_generate_qr_code(self):
        """Generate a QR code for the Serial Number."""
        for record in self:
            if not record.serial_number:
                raise ValidationError(_("The Serial Number is required to generate a QR Code."))
            
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=6,
                border=2,
            )
            qr.add_data(record.serial_number)
            qr.make(fit=True)
            
            # Convert QR Code to Image
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            qr_code_data = base64.b64encode(buffer.getvalue())
            record.qr_code = qr_code_data
            if record.qr_code:
                raise ValidationError(_("QR Already Generated"))