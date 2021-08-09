from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('tax_repartition_line_id.invoice_tax_id', 'tax_repartition_line_id.refund_tax_id', 'tax_repartition_line_id.payment_tax_id')
    def _compute_tax_line_id(self):
        """ tax_line_id is computed as the tax linked to the repartition line creating
        the move.
        """
        for record in self:
            rep_line = record.tax_repartition_line_id
            # A constraint on account.tax.repartition.line ensures both those fields are mutually exclusive
            record.tax_line_id = rep_line.invoice_tax_id or rep_line.refund_tax_id or rep_line.payment_tax_id
