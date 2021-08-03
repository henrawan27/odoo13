from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def default_get(self, vals):
        # company_id is added so that we are sure to fetch a default value from it to use in repartition lines, below
        rslt = super(AccountTax, self).default_get(vals)

        company_id = rslt.get('company_id')
        company = self.env['res.company'].browse(company_id)

        if not company.use_custom_cash_basis_taxes:
            return rslt

        if 'payment_repartition_line_ids' in vals:
            rslt['payment_repartition_line_ids'] = [
                (0, 0, {'repartition_type': 'base', 'factor_percent': 100.0, 'tag_ids': [], 'company_id': company_id, 'country_id': company.country_id.id}),
                (0, 0, {'repartition_type': 'tax', 'factor_percent': 100.0, 'tag_ids': [], 'company_id': company_id, 'country_id': company.country_id.id}),
            ]

        return rslt

    payment_repartition_line_ids = fields.One2many(string="Repartition for Payments", comodel_name="account.tax.repartition.line", inverse_name="payment_tax_id", copy=True, help="Repartition when the tax is used on an payment")
    tax_exigibility = fields.Selection(selection_add=[('on_payment_custom', 'Based on Payment (Custom)')])


class AccountTaxRepartitionLine(models.Model):
    _inherit = "account.tax.repartition.line"

    payment_tax_id = fields.Many2one(comodel_name='account.tax', help="The tax set to apply this repartition on payments.")
