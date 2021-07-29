from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mpn_sequence = fields.Boolean(string='MPN Sequence as Default', related='company_id.mpn_sequence', readonly=False)
