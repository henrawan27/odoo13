from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    account_opening_move_id = fields.Many2one('account.move', related='company_id.account_opening_move_id')
    create_as_opening = fields.Boolean(string='Create as Opening')
    mark_reconcile = fields.Boolean(string='Mark Reconcile')

    @api.model
    def create(self, vals):
        record = super(AccountMove, self).create(vals)
        if vals.get('create_as_opening'):
            company = self.env.company
            if not company.account_opening_move_id:
                record.update({'name': _('Opening Journal Entry')})
                company.account_opening_move_id = record.id
        return record
