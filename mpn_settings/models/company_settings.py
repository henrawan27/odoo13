from odoo import models, api


<<<<<<< HEAD
class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.model
    def get_mpn_settings(self):

        # delete unused journals
        journals = self.env['account.journal'].search([])
        move_journals = self.env['account.move'].search([]).mapped('journal_id')
        unused_journals = journals - move_journals

        if unused_journals:
            unused_journals.unlink()

        # delete unused accounts
        accounts = self.env['account.account'].search([
            ('name', 'in', ['Bank', 'Cash', 'Liquidity Transfer'])
        ])
        if accounts:
            accounts.unlink()

        # set price digits
        product_price = self.env['decimal.precision'].search([('name', '=', 'Product Price')])
        product_price.write({'digits': 3})

        # install Indonesian language
        language = self.env['base.language.install'].create({'lang': 'id_ID', 'overwrite': True})
        language.lang_install()
=======
class CompanySettings(models.TransientModel):
    _name = 'extra.company.settings'
    _description = 'Company Settings'

    @api.model
    def get_company_settings(self):
        product_price = self.env['decimal.precision'].search([('name', '=', 'Product Price')])
        product_price.write({'digits': 3})
>>>>>>> 2f1d31a4a7c3e8cba3cbb07060385a360e43804a
