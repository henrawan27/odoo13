from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    price_subtotal_rounded = price_subtotal = fields.Monetary(string='Rounding')

    @api.onchange('price_subtotal_rounded')
    def _onchange_price_subtotal_rounded(self):
        if self.quantity:
            self.price_unit = self.price_subtotal_rounded / self.quantity

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        res = super(AccountMoveLine, self)._get_price_total_and_subtotal_model(price_unit, quantity, discount, currency, product, partner, taxes, move_type)
        res['price_subtotal_rounded'] = res.get('price_subtotal', 0)
        return res
