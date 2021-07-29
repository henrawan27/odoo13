from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    parent_mark_reconcile = fields.Boolean(string='Parent Mark Reconcile', related='move_id.mark_reconcile')
    mark_reconcile = fields.Boolean(string='Mark Reconcile')
    # price_subtotal_rounded = fields.Monetary(string='Rounding')
    #
    # @api.onchange('price_subtotal_rounded')
    # def _onchange_price_subtotal_rounded(self):
    #     if self.quantity:
    #         self.price_unit = self.price_subtotal_rounded / self.quantity
    #
    # @api.model
    # def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
    #     res = super(AccountMoveLine, self)._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
    #     res['price_subtotal_rounded'] = res.get('price_subtotal', 0.0)
    #     return res
