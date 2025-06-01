from odoo import _, api, fields, models, tools


class OsoulHumanResources(models.Model):
    _inherit = 'hr.employee'

    management_name = fields.Many2one(comodel_name="osoul.hr.managements", string="Management", ondelete='restrict', tracking=True)
   
    
    # HUMAN RESOURCES
    employment_no = fields.Char(string="Employment No", tracking=True)
    #emp_no_id = fields.Many2one('osoul.security.supplier.enter.permission',string="Emp No", tracking=True)
    e_name = fields.Many2one(string='name',comodel_name='osoul.security.supplier.enter.permission',ondelete='restrict')
    hire_date = fields.Date(string="Hire Date", tracking=True)
    join_date = fields.Date(string="Join Date", tracking=True)
    contracting_party = fields.Many2one(comodel_name="osoul.hr.contractors", string="Contracting Party", ondelete='restrict', tracking=True)
    status = fields.Selection([('active', 'Active'), ('not_active', 'Not Active')], string="Active")
    nationality = fields.Char(string="Nationality", tracking=True)
    degree = fields.Char(string="Degree", tracking=True)
    category = fields.Char(string="Category", tracking=True)
    # PRIVATE INFORMATION
    citizen = fields.Selection([('citizen', 'Citizen'), ('not_citizen', 'Not Citizen')], string="Citizen", tracking=True)
    religion = fields.Selection([('muslim', 'Muslim'), ('not_muslim', 'Not Muslim')], string="Religion", tracking=True)
    # ACCOMMODATION
    host_accom =  fields.Selection([('hosted', 'Hosted'),('not_hosted', 'Not Hosted')],string="Housing status",default="not_hosted")
    housing_location = fields.Selection([('osoul_poultry', 'Osoul Poultry'), ('osoul_hatchery', 'Osoul Hatchery'),
                                         ('abha_accommodation', 'Abha Accommodation'), ('jeddah_accommodation', 'Jeddah Accommodation'),
                                         ('bin_hashbal', 'Bin Hashbal')], string="Housing Location")
    # SECURITY 
    in_out_status = fields.Selection([('draft', 'Draft'),
                                      ('inside_osoul', 'Inside Osoul'),
                                      ('outside_osoul', 'Outside Osoul')], default="draft", readonly=True, tracking=True)
                                      
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        domain = args + ['|', '|', ("employment_no", operator, name), ("name", operator, name), ("country_id.name", operator, name)]
        employees = self.search(domain, limit=limit)
        return employees.name_get()
    
    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.employment_no})" if record.employment_no else record.name
            result.append((record.id, name))
        return result
        