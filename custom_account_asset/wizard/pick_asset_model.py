from odoo import models, fields


class PickAssetModels(models.TransientModel):
    _name = 'pick.asset.model'
    _description = 'Pick Asset Models'

    account_id = fields.Many2one('account.account', string='Fixed Account')
    asset_model_id = fields.Many2one('account.asset', string='Asset Model', domain="[('state', '=', 'model'), ('account_asset_id', '=', account_id)]", required=True)

    def action_confirm(self):
        context = self.env.context.copy()
        if context.get('default_account_id'):
            del context['default_account_id']
        account_move_line = self.env['account.move.line'].browse(context.get('active_id'))