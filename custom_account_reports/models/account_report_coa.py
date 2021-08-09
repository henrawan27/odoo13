from odoo import models, api


class AccountChartOfAccountReport(models.AbstractModel):
    _inherit = "account.coa.report"

    @api.model
    def _get_lines(self, options, line_id=None):
        lines = super(AccountChartOfAccountReport, self)._get_lines(options, line_id=line_id)
        return lines
