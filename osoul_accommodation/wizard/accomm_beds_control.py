from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError

class AccommBedsControl(models.TransientModel):
    _name = "osoul.accommodation.beds.control.wizard"

    room_id = fields.Many2one(comodel_name='osoul.accommodation.room', string='Room', required=True,)
    bed_count = fields.Integer(string='Bed Count', required=True,)
    total_residents = fields.Integer(related='room_id.total_residents', string="Total Residants")
    operation_type = fields.Selection([('increase','Increase Beds'),('reduce','Reduce Beds'),], default="increase", required=True)

    def modify_beds(self):
        self.ensure_one()
        if self.room_id:
            if self.operation_type == "increase":
                increase = self.bed_count + self.room_id.total_beds
                self.room_id.total_beds = increase
                self.room_id.onchange_field()
            elif self.operation_type == "reduce":
                if self.room_id.total_beds < self.bed_count:
                    raise ValidationError(_("Operation Error: Cannot reduce beds more than total beds available."))
                else:
                    reduce = self.room_id.total_beds - self.bed_count
                    if reduce > 0 and reduce > self.room_id.total_residents:
                        raise ValidationError(_("Operation Error: Cannot reduce beds below the number of residents."))
                    else:
                        self.room_id.total_beds = reduce
                        self.room_id.onchange_field()
                        