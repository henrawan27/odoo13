from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    mpn_sequence = fields.Boolean(string='MPN Sequence as Default')
