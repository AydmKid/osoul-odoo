from odoo import models, fields, api
import base64
import pandas as pd
from io import BytesIO
import logging

_logger = logging.getLogger(__name__)


class FileDashboard(models.Model):
    _name = 'file.dashboard'
    _description = 'File Dashboard'

    name = fields.Char(string='File Name', required=True)
    data = fields.Binary(string='File', attachment=True)
    file_type = fields.Selection([('import', 'Import'), ('export', 'Export')], string='Type', default='import')
    import_date = fields.Datetime(string='Import Date', default=fields.Datetime.now)
    line_ids = fields.One2many('file.dashboard.line', 'file_dashboard_id', string='File Data')

    def import_from_excel(self):
        """Import data from Excel and populate file.dashboard.line model."""
        if not self.data:
            _logger.error("No file data found to import.")
            return

        file_data = base64.b64decode(self.data)
        df = pd.read_excel(BytesIO(file_data), engine='openpyxl')

        # Clear previous data (if needed)
        self.line_ids.unlink()

        # Log column names for verification
        _logger.info(f"Columns found in file: {df.columns.tolist()}")

        # Ensure 'Name' column exists
        if 'Name' not in df.columns:
            _logger.error("Column 'Name' not found in the imported file.")
            return

        # Process each row and create a line in file.dashboard.line
        for _, row in df.iterrows():
            self.env['file.dashboard.line'].create({
                'file_dashboard_id': self.id,
                'column1': row.get('Column1', 'N/A'),
                'column2': row.get('Column2', 'N/A'),
                'name': row.get('Name', 'Unnamed')
            })


class FileDashboardLine(models.Model):
    _name = 'file.dashboard.line'
    _description = 'File Dashboard Line'

    file_dashboard_id = fields.Many2one('file.dashboard', string='Dashboard File', ondelete='cascade')
    name = fields.Char(string='Name')
    column1 = fields.Char(string='Column 1')
    column2 = fields.Char(string='Column 2')
