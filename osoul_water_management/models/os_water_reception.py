from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta
import logging
import requests

class OsoulosWaterReception(models.Model):
    _name = 'osoul.water.reception'
    _description = 'Water Delivery Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'trip_no'

    # Tanker Vehicle Information
    trip_no = fields.Char(string='Reference', copy=False, readonly=True, store=True)
    owner_id = fields.Many2one(comodel_name="osoul.water.vendor", string="Vendor", readonly=True, store=True, ondelete='restrict')
    vehicle_id = fields.Many2one('osoul.water.tanker', string='Vehicle', readonly=True, store=True, ondelete='restrict')
    capacity = fields.Float(string='Capacity', related='vehicle_id.capacity', store=True)
    driver_id = fields.Many2one('osoul.tanker.driver', string='Driver Name', readonly=True, store=True, ondelete='restrict')
    driver_phone = fields.Char(related="driver_id.phone", string='Driver Phone', readonly=True, store=True)

    # Entry Information
    security_guard = fields.Many2one(comodel_name="res.users", string="Security Guard", readonly=True, store=True)
    security_phone = fields.Char(string='Security Phone', readonly=True, store=True)
    entry_time = fields.Datetime(string='Entry Time', readonly=True, store=True)
    exiting_time = fields.Datetime(string='Exiting Time', readonly=True, store=True)
    permission = fields.Selection(
        [('not_authorized', 'Not Authorized'), ('authorized_in', 'Authorized In'),
         ('authorized_out', 'Authorized Out')],
        default='not_authorized', readonly=True, tracking=True, store=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('authorization', 'Authorization'), ('permit_enter', 'Permit Enter'),
         ('inside_osoul', 'Inside Osoul'), ('filling_start', 'Filling Start'), 
         ('filling_over', 'Filling Over'), ('permit_exit', 'Permit Exit'), 
         ('outside_osoul', 'Outside Osoul')], default='draft', tracking=True)

    # Water Information
    water_type = fields.Selection(
        [('high_salinity', 'High Salinity'), ('low_salinity', 'Low salinity'),
         ('residential_desalination_water', 'Residential desalination water'),
         ('commercial_desalinated_water', 'Commercial desalinated water'),
         ('desalinated_water_with_tax', 'Desalinated water with tax')], tracking=True)
    filling_tanker = fields.Selection([('raw', 'Raw'), ('filtring', 'Filtring')], tracking=True)
    water_tds = fields.Float(string="TDS", default=0.0, tracking=True)
    start_tanker_filling = fields.Datetime(string="Start Filling Time", readonly=True, store=True)
    stop_tanker_filling = fields.Datetime(string="Stop Filling Time", readonly=True, store=True)
    tank_filling_period = fields.Char(string="Tank Filling Period", compute="_compute_tank_filling_period")

#===========================================================================================================================#
# WATER COUNTERS BEFORE - AFTER
#===========================================================================================================================#

    # Water Flow Counters
    # Water Flow Counters Last Read
    prev_read_cone = fields.Float(string="PRead C.One", store=True)
    prev_read_ctwo = fields.Float(string="PRead C.Two", store=True)
    prev_read_cthree = fields.Float(string="PRead C.Three", store=True)

    filling_station = fields.Selection(
        [('a', 'A Station'), ('b', 'B Station'), ('c', 'C Station'),
         ('d', 'D Station'), ('e', 'E Station'), ('f', 'F Station'), ('g', 'G Station')], tracking=True)
    curr_read_cone = fields.Float(string="CRead C.One", tracking=True, readonly=True)
    curr_read_ctwo = fields.Float(string="CRead C.Two", tracking=True, readonly=True)
    curr_read_cthree = fields.Float(string="CRead C.Three", tracking=True, readonly=True)

    filled_water_cone = fields.Float(string="Filled WC.One", compute="_compute_count_one", store=True)
    filled_water_ctwo = fields.Float(string="Filled WC.Two", compute="_compute_count_two", store=True)
    filled_water_cthree = fields.Float(string="Filled WC.Three", compute="_compute_count_three", store=True)
    total_filled_water = fields.Float(string="T.Filled Water", compute="_compute_total_filled_water", store=True)

#===========================================================================================================================#
# 
#===========================================================================================================================#

    # Water Pricing
    load_difference = fields.Float(string="Load Difference", compute="_compute_load_difference", store=True)
    water_price_id = fields.Many2one('osoul.water.price', string="Water Price", compute="_compute_water_price", store=True)
    ton_price = fields.Float(related="water_price_id.ton_price", string="Price Per Liter", readonly=True, store=True)
    total_cost = fields.Float(string="Cost", compute="_compute_cost", store=True)

#===========================================================================================================================#
# FILLED WATER COUNTERS - CONE - CTWO - CTHREE
#===========================================================================================================================#
    
    
    @api.depends('curr_read_cone', 'prev_read_cone', 'curr_read_ctwo', 'prev_read_ctwo', 'curr_read_cthree', 'prev_read_cthree')
    def _compute_count_one(self):
        for record in self:
            # CONE COMPUTE
            if record.curr_read_cone and record.prev_read_cone:
                cone = record.curr_read_cone - record.prev_read_cone
                if cone <0:
                    raise ValidationError(_("Current Counter Can Not be Smaller Than Prev"))
                else:
                    record.filled_water_cone = cone
            
            # CTWO COMPUTE
            if record.curr_read_ctwo and record.prev_read_ctwo:
                ctwo = record.curr_read_ctwo - record.prev_read_ctwo
                if ctwo <0:
                    raise ValidationError(_("Current Counter Can Not be Smaller Than Prev"))
                else:
                    record.filled_water_ctwo = ctwo

            # CTHREE COMPUTE
            if record.curr_read_cthree and record.prev_read_cthree:
                cthree = record.curr_read_cthree - record.prev_read_cthree
                if cthree <0:
                    raise ValidationError(_("Current Counter Can Not be Smaller Than Prev"))
                else:
                    record.filled_water_cthree = cthree

    # CALCULATE TOTAL FILLED WATER.
    @api.depends("filled_water_cone", "filled_water_ctwo", "filled_water_cthree")
    def _compute_total_filled_water(self):
        for record in self:
            record.total_filled_water = sum([record.filled_water_cone, record.filled_water_ctwo, record.filled_water_cthree])


    # CALLING THE LAST READING FORM COUNTERS CLASSs
    @api.onchange("filling_station")
    def _onchange_filling_station(self):
        if self.filling_station:
            counters = self.env['osoul.water.counter'].search(
                [('filling_station', '=', self.filling_station)], 
                order="filling_date desc",
                limit=1
            )

            if counters:
                self.prev_read_cone = counters.curr_read_cone
                self.prev_read_ctwo = counters.curr_read_ctwo
                self.prev_read_cthree = counters.curr_read_cthree
            else:
                self.prev_read_cone = 0
                self.prev_read_ctwo = 0
                self.prev_read_cthree = 0

#===========================================================================================================================#
# 
#===========================================================================================================================#

    @api.depends('start_tanker_filling', 'stop_tanker_filling')
    def _compute_tank_filling_period(self):
        for record in self:
            if record.start_tanker_filling and record.stop_tanker_filling:
                if record.start_tanker_filling > record.stop_tanker_filling:
                    record.tank_filling_period = "Invalid Period"
                else:
                    filling_duration = record.stop_tanker_filling - record.start_tanker_filling
                    total_seconds = int(filling_duration.total_seconds())
                    hours, remainder = divmod(total_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    record.tank_filling_period = f"{hours:02}:{minutes:02}:{seconds:02}"
            else:
                record.tank_filling_period = "N/A"

# ========================================================================================================================= #
# WATER COST CALCULATIONS #
# ========================================================================================================================= #
    @api.depends("water_type")
    def _compute_water_price(self):
        for record in self:
            price = self.env['osoul.water.price'].search([("name", "=", record.water_type)])
            record.water_price_id = price

    @api.depends('total_filled_water', 'capacity')
    def _compute_load_difference(self):
        for record in self:
            if record.total_filled_water and record.capacity:
                record.load_difference = record.capacity - record.total_filled_water

    @api.depends("load_difference", "ton_price", "capacity")
    def _compute_total_cost(self):
        for record in self:
            loading_limit = 500
            if record.load_difference and record.load_difference <= loading_limit:
                record.total_cost = (record.ton_price / 1000) * record.capacity
            else:
                record.total_cost = 0
# ========================================================================================================================= #
# BUTTONS #
# ========================================================================================================================= #
    def action_authorized_in(self):
        for record in self:
            record.state = "permit_enter"
            record.permission = "authorized_in"
            tanker_entry = self.env['osoul.water.tanker.entry'].search([('trip_no', '=', record.trip_no)], limit=1)
            if tanker_entry:
                tanker_entry.write({'permission': 'authorized_in', 'state': 'permit_enter'})

            # Send WhatsApp notification to security guard
            if record.security_guard and record.security_phone:
                instance_id = "instance103098"
                token = "dm86hbcidw154pdh"
                api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

                message_body = f"""
Hi {record.security_guard.name},

The tanker with the following details has been authorized for entry:
- Trip No: {record.trip_no}
- Vendor: {record.owner_id.name}
- Vehicle: {record.vehicle_id.display_name}
- Driver: {record.driver_id.name}
- Time: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please proceed with the necessary actions.
Osoul Water Management.
"""

                payload = {
                    'token': token,
                    'to': record.security_phone,
                    'body': message_body.strip()
                }

                try:
                    response = requests.post(api_url, json=payload, timeout=10)
                    if response.status_code != 200:
                        raise UserError(_("Failed to send WhatsApp message to the security guard. Response: %s") % response.text)
                except requests.RequestException as e:
                    raise UserError(_("Error while sending WhatsApp message to the security guard: %s") % str(e))
                
    def action_start_tanker_filling(self):
        for record in self:
            if record.water_tds == 0:
                raise UserError("Enter the TDS before starting filling.")
            record.start_tanker_filling = fields.Datetime.now()
            record.state = "filling_start"

    def action_stop_tanker_filling(self):
        for record in self:
            if any(counter <= 0 for counter in [record.curr_read_cone, record.curr_read_ctwo, record.curr_read_cthree]):
                raise UserError("Counters must be greater than zero before stopping filling.")
            record.state = "filling_over"
            record.stop_tanker_filling = fields.Datetime.now()
            self.env['osoul.water.counter'].create({
                'trip_no': record.trip_no,
                'vehicle_id': record.vehicle_id.id,
                'owner_id': record.owner_id.id,
                'driver_id': record.driver_id.id,
                'water_type': record.water_type,
                'filling_station': record.filling_station,
                'curr_read_cone': record.curr_read_cone,
                'curr_read_ctwo': record.curr_read_ctwo,
                'curr_read_cthree': record.curr_read_cthree,
                'filled_water_cone': record.filled_water_cone,
                'filled_water_ctwo': record.filled_water_ctwo,
                'filled_water_cthree': record.filled_water_cthree,
                'total_filled_water': record.total_filled_water,
                'filling_date': fields.Datetime.now(),
                'total_cost': record.total_cost,
            })

    def action_authorized_out(self):
        for record in self:
            record.state = "permit_exit"
            record.permission = "authorized_out"
            tanker_exit = self.env['osoul.water.tanker.entry'].search([('trip_no', '=', record.trip_no)], limit=1)
            if tanker_exit:
                tanker_exit.write({'permission': 'authorized_out', 'state': 'permit_exit'})

            # Send WhatsApp notification to security guard
            if record.security_guard and record.security_phone:
                instance_id = "instance103098"
                token = "dm86hbcidw154pdh"
                api_url = f"https://api.ultramsg.com/{instance_id}/messages/chat"

                message_body = f"""
Hi {record.security_guard.name},

The tanker with the following details has been authorized for exit:
- Trip No: {record.trip_no}
- Vendor: {record.owner_id.name}
- Vehicle: {record.vehicle_id.display_name}
- Driver: {record.driver_id.name}
- Time: {fields.Datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please proceed with the necessary actions.
Osoul Water Management.
"""

                payload = {
                    'token': token,
                    'to': record.security_phone,
                    'body': message_body.strip()
                }

                try:
                    response = requests.post(api_url, json=payload, timeout=10)
                    if response.status_code != 200:
                        raise UserError(_("Failed to send WhatsApp message to the security guard. Response: %s") % response.text)
                except requests.RequestException as e:
                    raise UserError(_("Error while sending WhatsApp message to the security guard: %s") % str(e))
                
# ========================================================================================================================= #
# WATER PRICE LIST CLASS #
# ========================================================================================================================= #
                
from odoo import models, fields, api

class OsoulosWaterPrice(models.Model):
    _name = 'osoul.water.price'
    _description = 'Water Type Price List'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Selection(
        [('high_salinity', 'High Salinity'), 
         ('low_salinity', 'Low salinity'),
         ('residential_desalination_water', 'Residential desalination water'),
         ('commercial_desalinated_water', 'Commercial desalinated water'),
         ('desalinated_water_with_tax', 'Desalinated water with tax')], 
        string="Water Type", required=True, tracking=True, translate=True
    )
    ton_price = fields.Float(string="Ton Price", required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.company.currency_id,
                                  required=True, readonly=True)

    _sql_constraints = [
        ('unique_water_type', 'unique(name)', 'Each water type must have a unique price entry.')
    ]

    @api.depends('name', 'ton_price', 'currency_id')
    def name_get(self):
        result = []
        for record in self:
            # Get the display name from the selection value
            water_type_display = dict(self._fields['name'].selection).get(record.name, '')
            # Add the price with the currency symbol
            price_display = f"{record.currency_id.symbol}{record.ton_price:.2f}"
            # Combine the two parts
            display_name = f"{water_type_display} [{price_display}]"
            result.append((record.id, display_name))
        return result