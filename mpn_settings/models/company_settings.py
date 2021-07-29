from odoo import models, api, modules
import base64
import xlrd


class CompanySettings(models.TransientModel):
    _name = 'extra.company.settings'
    _description = 'Company Settings'

    @api.model
    def get_company_settings(self):
        product_price = self.env['decimal.precision'].search([('name', '=', 'Product Price')])
        product_price.write({'digits': 3})
