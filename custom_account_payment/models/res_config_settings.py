from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    use_custom_cash_basis_taxes = fields.Boolean(string='Custom Cash Basis', related='company_id.use_custom_cash_basis_taxes', readonly=False)

    @api.onchange('tax_exigibility')
    def _onchange_tax_exigibility(self):
        super(ResConfigSettings, self)._onchange_tax_exigibility()
        if not self.tax_exigibility:
            self.use_custom_cash_basis_taxes = False
