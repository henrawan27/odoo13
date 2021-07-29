from odoo import models, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'R' + prefix
        if not self.env.company.mpn_sequence:
            return prefix + '/%(range_year)s/'
        return prefix + '/%(roman_month)s/%(range_year)s/'
