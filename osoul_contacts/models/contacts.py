from odoo import _, api, fields, models, tools

class OsoulContacts(models.Model):
    _inherit = "res.partner"

    supplier_name  = fields.Char()
    identity_no = fields.Char(string="Identity Number")
    in_out_state = fields.Selection([('draft','Draft'),('inside_osoul','Inside Osoul'),('outside_osoul','Out Osoul')], string="InOut Status", default="draft")
    noti_state  = fields.Selection([('notification_on', 'Notification On'),
                                    ('notification_off', 'Notification Off')])