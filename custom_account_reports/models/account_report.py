from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'

    def format_value(self, amount, currency=False, blank_if_zero=False):
        formatted = super(AccountReport, self).format_value(amount, currency=currency, blank_if_zero=blank_if_zero)
        if not self.env.company.report_minus_bracket:
            return formatted
        try:
            if '-' in formatted:
                return formatted.replace('-', '(') + ')'
            return formatted
        except TypeError:
            return formatted
