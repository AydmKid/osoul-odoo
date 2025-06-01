from odoo import _, api, fields, models, tools


class Cities(models.Model):
    _name = "countries.cities"
    _description = ""
    _rec_name = "city_name"

    city_name = fields.Char(string="City Name", translate=True)

    _sql_constraints = [
        ('unique_city_name', 'unique(city_name)', 'City name must be unique.')]