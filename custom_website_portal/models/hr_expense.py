from odoo import models, fields


class HRExpense(models.Model):
    _inherit = 'hr.expense'

    sale_id = fields.Many2one('sale.order', string='Sale Order')
