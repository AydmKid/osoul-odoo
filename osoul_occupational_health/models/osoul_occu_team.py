from odoo import _, api, fields, models, tools

class OsoulOccuTeam(models.Model):
    _name = 'osoul.occu.team'
    _description = 'Occupational Health Team'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name_id'
    _rec_name = 'name_id'

    name_id = fields.Many2one(comodel_name='hr.employee', string='Name', required=True, tracking=True)
    job_id = fields.Many2one(comodel_name='hr.job', related='name_id.job_id', string='Job Title')
    phone = fields.Char(string='Phone', related='name_id.mobile_phone', store=True)
    state = fields.Selection([
        ('draft', 'draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive')], string='Status', default='inactive', required=True, tracking=True)
    join_date = fields.Date(string='Join Date', readonly=True, tracking=True)
    end_date = fields.Date(string='End Date', readonly=True, tracking=True)
    total_days = fields.Integer(string='Total Days', compute='_compute_total_days', store=True, tracking=True)
    total_checkups = fields.Integer(string='Total Checkups', compute='_compute_total_checkups', store=True, tracking=True)

    # @api.depends('name_id')
    # def _compute_total_checkups(self):
    #     for rec in self:
    #         checkup_ids = self.env['osoul.occu.checkup'].search([('employee_id', '=', rec.name_id.id)])
    #         rec.total_checkups = len(checkup_ids)

    @api.depends('join_date', 'end_date')
    def _compute_total_days(self):
        for rec in self:
            if rec.join_date and rec.end_date:
                rec.total_days = (rec.end_date - rec.join_date).days

    def action_active(self):
        self.write({'state': 'active'}) # This is the line that I want to change
        self.write({'join_date': fields.Date.today()})
        self.end_date = False
        self.total_days = False
        self.total_checkups = False

    def action_inactive(self):      
        self.write({'state': 'inactive'}) # This is the line that I want to change
        self.write({'end_date': fields.Date.today()})