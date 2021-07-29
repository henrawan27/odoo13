from odoo import models, api, modules
import base64
import xlrd


class CompanySettings(models.TransientModel):
    _name = 'extra.company.settings'
    _description = 'Company Settings'

    @api.model
    def get_company_settings(self):

        # edit default cash journal
        cash_journal = self.env['account.journal'].search([
            ('name', '=', 'Cash'),
            ('type', '=', 'cash')
        ])
        if cash_journal:
            cash_journal[0].sequence_id.update({
                'name': 'Cash Sequence',
                'prefix': 'CASH/%(range_year)s/'
            })
            cash_journal[0].update({
                'name': 'Kas',
                'code': 'CASH',
                'default_debit_account_id': self.env.ref('mpn_chart_template_fix.a_x_111_01_001').id,
                'default_credit_account_id': self.env.ref('mpn_chart_template_fix.a_x_111_01_001').id,
            })

        # delete unused journal
        unused_journals = [('Bank', 'bank')]

        for journal_name, journal_type in unused_journals:
            journal = self.env['account.journal'].search([
                ('name', '=', journal_name),
                ('type', '=', journal_type)
            ])
            if journal:
                journal.unlink()

        # delete unused accounts
        unused_accounts = ['Bank', 'Cash', 'Liquidity Transfer']
        accounts = self.env['account.account'].search([
            ('name', 'in', unused_accounts)
        ])
        if accounts:
            accounts.unlink()

        # update company info
        company = self.env.company
        logo_path = modules.get_module_resource('mpn_account_fix', 'static/logo', 'mpn_logo.png')
        with open(logo_path, 'rb') as f:
            logo_bin = f.read()

        company.update({
            'name': 'MPN',
            'street': 'Jln. Soekarno-Hatta',
            'city': 'Bandung',
            'state_id': self.env.ref('base.state_id_jb')[0].id,
            'country_id': self.env.ref('base.id')[0].id,
            'zip': False,
            'phone': '021-9999 9999',
            'email': 'community@mpn.com',
            'website': 'http://www.mpn.com',
            'logo': base64.b64encode(logo_bin)
        })

        # install Indonesian language
        language = self.env['base.language.install'].create({'lang': 'id_ID', 'overwrite': True})
        language.lang_install()
