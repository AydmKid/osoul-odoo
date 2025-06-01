from odoo import _, api, fields, models, tools
from datetime import datetime
from odoo.exceptions import UserError
import random

class SecuritySupplierEnter(models.Model):
    _name = "osoul.security.supplier.enter"
    _description = ""
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "record_no"

    record_no = fields.Char(string="Record No", tracking=True)
    # SUPPLIER INFORMATION
    supplier_name = fields.Many2one('res.partner', string='Supplier Name', ondelete='restrict', tracking=True, readonly=True)
    identity_no_id = fields.Char(related='supplier_name.identity_no', string=" Identity No", readonly=True, tracking=True)
    mobile = fields.Char(related='supplier_name.mobile', string="Mobile", tracking=True)
    # PERMIT RELATION
    permission_code_id = fields.Many2one('osoul.security.supplier.enter.permission', string='Permission Code', compute="_compute_permission_code", tracking=True, store=True)
    permit_issuer_id = fields.Many2one(related='permission_code_id.permit_issuer_id', string="Permit Issuer", tracking=True)
    employment_no_id = fields.Char(related='permission_code_id.employment_no_id', string="Employment No", store=True, readonly=True ,tracking=True )
    department_id = fields.Many2one(related='permission_code_id.department_id', string="Department", tracking=True)
    supply_type_id = fields.Many2one(related='permission_code_id.supply_type_id', string="Supply Type", tracking=True)
    operation_type = fields.Selection(related='permission_code_id.operation_type', string="Operation Type", tracking=True)
    plate_no = fields.Char(related='permission_code_id.plate_no', string="Vehicle Plate No", tracking=True)
    plate_letters = fields.Char(related='permission_code_id.plate_letters', string="Vehicle Plate Letter", tracking=True)
    note = fields.Text(related='permission_code_id.note', string="Extra Note", tracking=True)
    permission_state = fields.Selection(related='permission_code_id.state', string="Permission Status", tracking=True)
    enter_exit_permission = fields.Selection(related='permission_code_id.enter_exit_permission', string="In-Out Allowed Status", tracking=True)
    # GATE AND TIMING INFORMATION
    entry_gate_id = fields.Many2one(string="Entering Gate", comodel_name="osoul.security.poultry.gates", ondelete="restrict", tracking=True)
    guard_in_entry_id = fields.Many2one(string="Entering Guard", comodel_name="res.users", ondelete="restrict", tracking=True)
    time_in = fields.Datetime(string="Entering Time", readonly=True, tracking=True)
    exit_gate_id = fields.Many2one(string="Exiting Gate", comodel_name="osoul.security.poultry.gates", ondelete="restrict", tracking=True)
    guard_in_exiting_id = fields.Many2one(string="Exiting Guard", comodel_name="res.users", ondelete="restrict", tracking=True)
    time_out = fields.Datetime(string="Exiting Time", readonly=True, tracking=True)
    time_spent_inside = fields.Char(string="Time Spent Inside", compute="_compute_time_spent_inside", store=True, tracking=True)
    state = fields.Selection([("draft", "Draft"),
                              ("inside_osoul", "Inside Osoul"),
                              ("outside_osoul", "Outside Osoul")], string="State", default="draft", tracking=True)
    progress = fields.Integer(string="Progress", compute="_compute_progress")
    gate_entry_record = fields.Char(string="Gate Entry Record", readonly=True, tracking=True)
   

    @api.depends('state')
    def _compute_progress(self):
        for rec in self:
            if rec.state == "draft":
                progress = random.randrange(5, 25)
            elif rec.state == "inside_osoul":
                progress = random.randrange(50, 75)
            elif rec.state == "outside_osoul":
                progress = 100
            else :
                progress = 0 
            rec.progress = progress


    @api.depends('supplier_name')
    def _compute_permission_code(self):
        for record in self:
            permission = self.env['osoul.security.supplier.enter.permission'].search([
                ('supplier_name', '=', record.supplier_name.id),
                ('state', '=', 'running')
            ], limit=1)
            record.permission_code_id = permission.id

    @api.depends("time_in", "time_out")
    def _compute_time_spent_inside(self):
        for record in self:
            if record.time_in and record.time_out:
                time_in = record.time_in
                time_out = record.time_out
                time_spent = time_out - time_in
                hours = time_spent.seconds // 3600
                minutes = (time_spent.seconds // 60) % 60
                seconds = time_spent.seconds % 60
                record.time_spent_inside = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                record.time_spent_inside = "00:00:00"

    def action_button_inside_osoul(self):
        self.state = "inside_osoul"
        self.time_in = datetime.now()
        self.guard_in_entry_id = self.env.user.id
        self.record_no = self.env["ir.sequence"].next_by_code("security_supplier_enter_sequence")
        self.permission_code_id.gate_entry_record = self.record_no
        self.permission_code_id.state = "expired"
        self.permission_code_id.enter_exit_permission = "exit_not_allowed"
        self.supplier_name.in_out_state = "inside_osoul"
        
        
       

    def action_button_outside_osoul(self):
        if self.enter_exit_permission == "exit_not_allowed":
            raise UserError(_('Ask Permit Issuer to Allowed Supplier to Exit'))
        else:
            self.state = "outside_osoul"
            self.time_out = datetime.now()
            self.guard_in_exiting_id = self.env.user.id
            self.permission_code_id.enter_exit_permission = "supplier_out"
            self.supplier_name.in_out_state = "outside_osoul"