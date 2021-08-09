from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_draft_number(self):
        for move in self:
            prefix, suffix = move.journal_id.sequence_id._get_prefix_suffix()
            move.draft_number = prefix + suffix

    def _compute_from_payment(self):
        for move in self:
            payment_ids = move.line_ids.mapped('payment_id')
            if payment_ids:
                move.from_payment = True
            else:
                move.from_payment = False

    account_opening_move_id = fields.Many2one('account.move', related='company_id.account_opening_move_id')
    create_as_opening = fields.Boolean(string='Create as Opening')
    draft_number = fields.Char(string='Draft Number', compute=_compute_draft_number)
    from_payment = fields.Boolean(string='From Customer Payments', compute=_compute_from_payment, store=True)

    origin_state = fields.Selection(selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ], string='Origin Status')

    @api.model
    def create(self, vals):
        record = super(AccountMove, self).create(vals)
        if vals.get('create_as_opening'):
            company = self.env.company
            if not company.account_opening_move_id:
                record.update({'name': _('Opening Journal Entry')})
                company.account_opening_move_id = record.id
        return record

    def post_origin_state(self):
        records = self.filtered(lambda x: x.origin_state == 'posted' and x.state == 'draft').sorted(key=lambda x: x.date)
        if records:
            records.post()

