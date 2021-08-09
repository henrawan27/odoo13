from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_active_invoices(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')

        # Check for selected invoices ids
        invoices = self.env['account.move']
        if active_ids and active_model == 'account.move':
            invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))

        return invoices

    def _default_tax_ids(self):
        if not self.env.company.use_custom_cash_basis_taxes:
            return []
        invoices = self._get_active_invoices()
        tax_ids = []
        for invoice in invoices:
            tax_ids += [(4, tax.id) for tax in invoice.line_ids.mapped('tax_ids').filtered(
                lambda tax: tax.tax_exigibility == 'on_payment_custom'
            )]
        return tax_ids

    def _default_dpp_amount(self):
        if not self.env.company.use_custom_cash_basis_taxes:
            return 0.0
        invoices = self._get_active_invoices()
        if len(invoices) == 1:
            return sum(invoices.mapped('amount_untaxed'))
        return 0.0

    def _get_dpp_amount(self):
        invoices = self._get_active_invoices()
        if not invoices:
            dpp_amount = self.amount * 100 / 110
        else:
            percent = (self.amount / sum(invoices.mapped('amount_total'))) * 100
            untaxed_amount = sum(invoices.mapped('amount_untaxed'))
            dpp_amount = (untaxed_amount * percent) / 100
        return dpp_amount

    @api.onchange('dpp_amount')
    def _onchange_dpp_amount(self):
        if self.tax_ids and not self.env.context.get('pass_check') and self.env.company.use_custom_cash_basis_taxes:
            if self.dpp_amount < 0.0:
                raise UserError(_("DPP Amount must be positive!"))
            # self.tax_amount = self._default_tax_amount()

    # @api.onchange('amount', 'currency_id')
    # def _onchange_amount(self):
    #     domain = super(AccountPayment, self)._onchange_amount()
    #     if self.env.company.use_custom_cash_basis_taxes:
    #         dpp_amount = self.tax_ids and self._get_dpp_amount() or 0.0
    #         self.with_context(pass_check=True).write({'dpp_amount': dpp_amount})
    #     return domain
    #
    @api.onchange('tax_ids')
    def _onchange_tax_ids(self):
        if self.env.company.use_custom_cash_basis_taxes:
            self._onchange_dpp_amount()

    def _prepare_payment_moves(self, return_tax_amount=False):
        moves = super(AccountPayment, self)._prepare_payment_moves()

        if not self.env.company.use_custom_cash_basis_taxes:
            return moves

        for i, payment in enumerate(self):
            if not payment.tax_ids:
                continue

            company_currency = payment.company_id.currency_id
            if payment.currency_id == company_currency:
                currency_id = False
            else:
                currency_id = payment.currency_id.id

            account_tax_amount = {}
            for tax in payment.tax_ids:

                tax_ids = []
                if tax.amount_type == 'group':
                    for tax_child in tax.children_tax_ids:
                        tax_ids.append(tax_child.id or tax_child._origin.id)
                else:
                    tax_ids.append(tax.id or tax._origin.id)

                repartition_line_ids = self.env['account.tax.repartition.line'].search([
                    ('payment_tax_id', 'in', tax_ids)
                ])

                for repr_line in repartition_line_ids:
                    if repr_line.repartition_type == 'base':
                        continue

                    tax_id = repr_line.payment_tax_id
                    if repr_line.account_id:
                        if tax_id.amount_type == 'percent':
                            amount = (payment.dpp_amount * ((tax_id.amount * repr_line.factor_percent) / 100)) / 100
                        elif tax_id.amount_type == 'fixed':
                            amount = (tax_id.amount * repr_line.factor_percent) / 100
                        else:
                            amount = (payment.amount * ((tax_id.amount * repr_line.factor_percent) / 100)) / 100

                        key = f"{repr_line.account_id.id}_{payment.partner_id.commercial_partner_id.id}_{tax_id.id}_{repr_line.id}"
                        if key not in account_tax_amount:
                            account_tax_amount[key] = amount
                        else:
                            account_tax_amount[key] += amount

            if return_tax_amount:
                return sum([v for k, v in account_tax_amount.items()])

            total_amount = 0.0
            if account_tax_amount:
                for key, balance in account_tax_amount.items():
                    account_id, partner_id, tax_id, repr_id = key.split('_')
                    tax_name = self.env['account.tax'].browse(eval(tax_id))[0].description

                    values = {
                        'currency_id': currency_id,
                        'payment_id': payment.id,
                        'account_id': eval(account_id),
                        'partner_id': eval(partner_id),
                        'tax_repartition_line_id': eval(repr_id),
                        'amount_currency': currency_id and -balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'name': tax_name,
                        'debit': balance < 0 and -balance or 0.0,
                        'credit': balance > 0 and balance or 0.0
                    }
                    total_amount += balance
                    moves[i]['line_ids'].append((0, 0, values))

            balance_amount = sum([x[-1]['debit'] - x[-1]['credit'] for x in moves[i]['line_ids'][2:]])

            if balance_amount > 0:
                if moves[i]['line_ids'][0][-1]['debit'] and not moves[i]['line_ids'][1][-1]['debit']:
                    moves[i]['line_ids'][0][-1]['debit'] -= balance_amount
                elif not moves[i]['line_ids'][0][-1]['debit'] and moves[i]['line_ids'][1][-1]['debit']:
                    moves[i]['line_ids'][1][-1]['debit'] -= balance_amount
            elif balance_amount < 0:
                if moves[i]['line_ids'][0][-1]['credit'] and not moves[i]['line_ids'][1][-1]['credit']:
                    moves[i]['line_ids'][0][-1]['credit'] += balance_amount
                elif not moves[i]['line_ids'][0][-1]['credit'] and moves[i]['line_ids'][1][-1]['credit']:
                    moves[i]['line_ids'][1][-1]['credit'] += balance_amount
        return moves

    def _compute_export_line_ids(self):
        for payment in self:
            moves = payment._prepare_payment_moves()

            # delete current export line
            current_export_ids = self.env['payment.export.line'].search([('payment_id', '=', payment.id)])
            if current_export_ids:
                current_export_ids.unlink()

            # create new export line
            export_ids = []
            for c1, c2, line in moves[0].get('line_ids', []):
                values = {
                    'name': line.get('name', ''),
                    'account_id': line.get('account_id', False),
                    'debit': line.get('debit', 0.0),
                    'credit': line.get('credit', 0.0)
                }
                line_id = self.env['payment.export.line'].create(values)
                export_ids.append(line_id.id)
            payment.export_line_ids = [(6, 0, export_ids)]

    def post_origin_state(self):
        records = self.filtered(lambda x: x.origin_state == 'posted' and x.state == 'draft').sorted(key=lambda x: x.payment_date)
        if records:
            records.post()

    tax_ids = fields.Many2many('account.tax', string='Taxes', domain="[('tax_exigibility', '=', 'on_payment_custom')]", default=_default_tax_ids)
    dpp_amount = fields.Monetary(string='DPP Amount', currency_field='currency_id', default=_default_dpp_amount)
    use_custom_cash_basis_taxes = fields.Boolean(related='company_id.use_custom_cash_basis_taxes', string='Use Custom Cash Basis Taxes')
    export_line_ids = fields.One2many('payment.export.line', 'payment_id', string='Export Lines', compute=_compute_export_line_ids)
    origin_state = fields.Selection([('draft', 'Draft'), ('posted', 'Validated'), ('sent', 'Sent'), ('reconciled', 'Reconciled'), ('cancelled', 'Cancelled')], string="Origin Status")


class PaymentExportLine(models.Model):
    _name = 'payment.export.line'
    _description = 'Payment'

    payment_id = fields.Many2one('account.payment', string='Payment', ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company.currency_id)
    name = fields.Char(string='Label')
    account_id = fields.Many2one('account.account', string='Account', index=True, ondelete="restrict", check_company=True, domain=[('deprecated', '=', False)])
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='currency_id')


class PaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def _prepare_payment_vals(self, invoices):
        values = super(PaymentRegister, self)._prepare_payment_vals(invoices)
        if self.env.company.use_custom_cash_basis_taxes:
            values.update({'dpp_amount': sum(invoices.mapped('amount_untaxed'))})
        return values
