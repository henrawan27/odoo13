from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    report_minus_bracket = fields.Boolean(related='company_id.report_minus_bracket', string='Display bracket as minus value', readonly=False)
