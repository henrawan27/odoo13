from odoo import models


class AccountFinancialHtmlReportLine(models.Model):
    _inherit = 'account.financial.html.report.line'

    def _format(self, value):
        formatted = super(AccountFinancialHtmlReportLine, self)._format(value)
        if not self.env.company.report_minus_bracket:
            return formatted
        try:
            if '-' in formatted['name']:
                formatted['name'] = formatted['name'].replace('-', '(') + ')'
                return formatted
            return formatted
        except TypeError:
            return formatted
