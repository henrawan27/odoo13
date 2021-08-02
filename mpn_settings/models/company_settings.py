from odoo import models, api


class CompanySettings(models.TransientModel):
    _name = 'extra.company.settings'
    _description = 'Company Settings'

    @api.model
    def get_company_settings(self):
        product_price = self.env['decimal.precision'].search([('name', '=', 'Product Price')])
        product_price.write({'digits': 3})

        currency = self.env['res.currency'].search([('name', '=', 'IDR')])
        currency.write({'rounding': 0.010000})
