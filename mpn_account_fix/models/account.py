from odoo import models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    def get_asset_accounts_type(self):
        return self.env.ref('account.data_account_type_fixed_assets') + self.env.ref('account.data_account_type_non_current_assets') + self.env.ref('mpn_chart_template_fix.data_account_type_aset_tetap')

    def get_deferred_revenue_accounts_type(self):
        return self.env.ref('account.data_account_type_current_liabilities') + self.env.ref('account.data_account_type_non_current_liabilities')

    def get_deferred_expense_accounts_type(self):
        return self.env.ref('account.data_account_type_current_assets') + self.env.ref('account.data_account_type_prepayments')
