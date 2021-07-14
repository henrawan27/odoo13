from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    parent_mark_reconcile = fields.Boolean(string='Parent Mark Reconcile', related='move_id.mark_reconcile')
    mark_reconcile = fields.Boolean(string='Mark Reconcile')
