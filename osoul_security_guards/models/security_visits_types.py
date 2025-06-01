from odoo import _, api, fields, models, tools


class SecurityVisitsTypes(models.Model):
    _name = "osoul.security.visits.types"
    _description = ""
    _rec_name = "visit_type"

    visit_code = fields.Char(string="Visit Code", translate=True)
    visit_type = fields.Char(string="Visit Type", translate=True)
    


    @api.model
    def create(self, vals):
        if vals.get("visit_code", "New"):
            vals["visit_code"] = (
                self.env["ir.sequence"].next_by_code("security_visits_types_sequence") or "New")
        return super(SecurityVisitsTypes, self).create(vals)