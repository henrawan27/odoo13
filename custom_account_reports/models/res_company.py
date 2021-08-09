from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_minus_bracket = fields.Boolean(string='Display Bracket As Minus Value')
