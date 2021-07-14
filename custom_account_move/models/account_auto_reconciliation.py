from odoo import models, fields


class AccountAutoReconciliation(models.TransientModel):
    _name = 'account.auto.reconciliation'
    _description = 'Account Auto Reconciliation'

    message = fields.Char(default="All move lines with mark_reconcile = True will be reconciled. You still be able to unreconcile them afterwards.")

    def action_auto_reconcile(self):

        partners = self.env['res.partner'].search([('active', '=', True)])
        currency_id = self.env.company.currency_id

        for partner in partners:

            move_lines = self.env['account.move.line'].search([
                ('partner_id', '=', partner.id),
                ('parent_state', '=', 'posted')
            ])

            for internal_type in ['receivable', 'payable']:

                debit_ids = move_lines.filtered(lambda x: x.account_internal_type == internal_type and x.debit > 0.0 and (x.parent_mark_reconcile or x.mark_reconcile))
                credit_ids = move_lines.filtered(lambda x: x.account_internal_type == internal_type and x.credit > 0.0 and (x.parent_mark_reconcile or x.mark_reconcile))

                amount_debit = sum(debit_ids.mapped('debit'))
                amount_credit = sum(credit_ids.mapped('credit'))
                if not currency_id.compare_amounts(amount_credit, amount_debit) and not currency_id.is_zero(amount_debit):
                    (debit_ids + credit_ids).reconcile()
