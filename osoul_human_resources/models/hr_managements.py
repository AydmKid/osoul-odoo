from odoo import models, fields

class OsoulHumanResourcesManagements(models.Model):
    _name = 'osoul.hr.managements'
    _description =""
    _rec_name ="management_name"

    management_code = fields.Integer(string="Management Code")
    management_name = fields.Char(string="Management Name")
    manager_name_id = fields.Many2one(string='Manager', comodel_name='hr.employee', ondelete='restrict')
    department_counter = fields.Integer(string="Total Departments", compute="_compute_total_departments", store=True)

    def _compute_total_departments(self):
        for rec in self:
            departments = self.env['hr.department'].search_count([('management_name_id','=',rec.management_name)])
            rec.department_counter = departments