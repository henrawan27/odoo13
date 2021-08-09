from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mpn_sequence = fields.Boolean(string='MPN Sequence as Default', related='company_id.mpn_sequence', readonly=False)

    def write(self, vals):
        res = super(ResConfigSettings, self).write(vals)
        journals = self.env['account.journal'].search([])
        for journal in journals:
            ranges = 'month' if self.mpn_sequence else 'year'
            journal.sequence_id.reset_range = ranges
        return res
