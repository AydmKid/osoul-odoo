from odoo import _, api, fields, models, tools

class OsoulTicktesSettings(models.Model):
    _name ="osoul.tickets.settings"
    _description = ""
    _rec_name = "issue_location"

    issue_location = fields.Char(string='Issue Location', translate=True)
    color = fields.Integer(string="Color")

    _sql_constraints = [
        ('unique_issue_location', 'unique(issue_location)', 'The issue location must be unique.')
    ]