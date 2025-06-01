from odoo import _, api, fields, models, tools , exceptions
from odoo.exceptions import ValidationError
from datetime import datetime , timedelta
from lxml import etree

class AccommContracts(models.TransientModel):
    _name = "osoul.accommodation.contrats.wizard"
    _description = 'Accommodation Contract Wizard'
    _inherit = 'mail.thread', 'mail.activity.mixin'
    _rec_name = "building_location"

    is_tenant = fields.Boolean(string="Is Tenant",tracking=True)
    rent_value = fields.Integer(string="Rent value",tracking=True)
    difference_in_days = fields.Integer(string='Remaining Days', compute="_compute_difference_in_days", store=True ,readonly=True,tracking=True)
    promissory_note_copy = fields.Binary(string="Contract Copy",tracking=True)
    start_date_decade = fields.Date(string='Start Date', store=True, tracking=True)
    end_date_decade = fields.Date(string='End Date', store=True, tracking=True)
    building_id = fields.Many2one('osoul.accommodation.building.dash', string='Building',tracking=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('contract_running', 'Contract Running'),
        ('contract_expired', 'Contract Expired')
    ], string="State", default="draft" ,tracking=True)

    payment_mechanism = fields.Selection([
        ('monthly', 'Monthly'),
        ('every_three_months', 'Every Three Months'),
        ('every_six_months ', 'Every Six Months'),
        ('every_year ', 'Every Year')
    ], string="Payment Mechanism",  tracking=True)

    building_location = fields.Selection([
        ('osoul_poultry', 'Osoul Poultry'),
        ('operation_office', 'Operation Office'),
        ('osoul_hatchery', 'Osoul Hatchery'),
        ('osoul_jeddah', 'Osoul Jeddah'),
        ('osoul_jizan', 'Osoul Jizan'),
        ('osoul_abha', 'Osoul Abha')
    ], string="Contract Location" , required=True)

    

    

    # RUNNING BUTTON
    def action_running_contract(self):
        self.state = "contract_running"


    # RUNNING Finsh
    def action_finsh_contract(self):
        self.state = "contract_expired"
    
    

    @api.model
    def name_get(self):
        result = []
        for record in self:
            name = record.building_location
            if name:
                result.append((record.id, dict(self.fields_get(allfields=['building_location'])['building_location']['selection'])[name]))
            else:
                result.append((record.id, _('(No Location)')))
        return result

    def create_contract(self):
        # Use self.building_location and self.building_id to access the passed parameters
        # Create the contract based on the received data
        # You can process the parameters here, create records, etc.
        print(f"Building Location: {self.building_location}")
        print(f"Building ID: {self.building_id}")
        return True


    @api.depends('start_date_decade', 'end_date_decade')
    def _compute_difference_in_days(self):
        for record in self:
            if record.start_date_decade and record.end_date_decade:
                start_date = fields.Date.from_string(record.start_date_decade)
                end_date = fields.Date.from_string(record.end_date_decade)
                record.difference_in_days = (end_date - start_date).days
            else:
                record.difference_in_days = 0

    @api.model
    def _cron_update_difference_in_days(self):
        records = self.search([])
        for record in records:
            record._compute_difference_in_days()