from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    use_custom_cash_basis_taxes = fields.Boolean(string='Use Custom Cash Basis Taxes')
