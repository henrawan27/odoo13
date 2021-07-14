# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools import format_date
from collections import defaultdict
from odoo.exceptions import UserError

MAX_NAME_LENGTH = 50


class AssetReport(models.AbstractModel):
    _inherit = 'account.assets.report'

    def open_asset_correction(self, options, params=None):
        active_id = int(params.get('id').split('_')[-1])
        line = self.env['account.asset.correction'].browse(active_id)
        return {
            'name': line.ref,
            'type': 'ir.actions.act_window',
            'res_model': 'account.asset.correction',
            'view_mode': 'form',
            'view_id': False,
            'views': [(False, 'form')],
            'res_id': line.id,
        }

    def _get_lines(self, options, line_id=None):
        options['self'] = self
        lines = []
        total = [0] * 9
        asset_lines = self._get_assets_lines(options)
        parent_lines = []
        children_lines = defaultdict(list)
        for al in asset_lines:
            if al['parent_id']:
                children_lines[al['parent_id']] += [al]
            else:
                parent_lines += [al]
        for al in parent_lines:

            if al['asset_method'] == 'linear' and al['asset_method_number']:  # some assets might have 0 depreciations because they dont lose value
                asset_depreciation_rate = ('{:.2f} %').format((100.0 / al['asset_method_number']) * (12 / int(al['asset_method_period'])))
            elif al['asset_method'] == 'linear':
                asset_depreciation_rate = ('{:.2f} %').format(0.0)
            else:
                asset_depreciation_rate = ('{:.2f} %').format(float(al['asset_method_progress_factor']) * 100)

            asset_id = self.env['account.asset'].browse([al['asset_id']])[0]
            if asset_id.compute_asset_based_opening and asset_id.amount_opening:
                al['depreciated_start'] = abs(asset_id.amount_opening) + al['depreciation']
                al['depreciated_end'] = al['depreciated_start'] + al['remaining_start'] - al['remaining_end']

            depreciation_opening = al['depreciated_start'] - al['depreciation']
            depreciation_closing = al['depreciated_end']
            depreciation_minus = 0.0

            opening = (al['asset_acquisition_date'] or al['asset_date']) < fields.Date.to_date(options['date']['date_from'])
            asset_opening = al['asset_original_value'] if opening else 0.0
            asset_add = 0.0 if opening else al['asset_original_value']
            asset_minus = 0.0

            for child in children_lines[al['asset_id']]:
                depreciation_opening += child['depreciated_start'] - child['depreciation']
                depreciation_closing += child['depreciated_end']

                opening = (child['asset_acquisition_date'] or child['asset_date']) < fields.Date.to_date(options['date']['date_from'])
                asset_opening += child['asset_original_value'] if opening else 0.0
                asset_add += 0.0 if opening else child['asset_original_value']

            depreciation_add = depreciation_closing - depreciation_opening
            asset_closing = asset_opening + asset_add

            if al['asset_state'] == 'close' and al['asset_disposal_date'] and al['asset_disposal_date'] < fields.Date.to_date(options['date']['date_to']):
                depreciation_minus = depreciation_closing
                depreciation_closing = 0.0
                depreciation_opening += depreciation_add
                depreciation_add = 0
                asset_minus = asset_closing
                asset_closing = 0.0

            asset_gross = asset_closing - depreciation_closing

            total = [x + y for x, y in zip(total, [asset_opening, asset_add, asset_minus, asset_closing, depreciation_opening, depreciation_add, depreciation_minus, depreciation_closing, asset_gross])]

            id = "_".join([self._get_account_group(al['account_code'])[0], str(al['asset_id'])])
            name = str(al['asset_name'])
            line = {
                'id': id,
                'level': 1,
                'name': name if len(name) < MAX_NAME_LENGTH else name[:MAX_NAME_LENGTH - 2] + '...',
                'columns': [
                    {'name': al['asset_acquisition_date'] and format_date(self.env, al['asset_acquisition_date']) or '', 'no_format_name': ''},  # Caracteristics
                    {'name': al['asset_date'] and format_date(self.env, al['asset_date']) or '', 'no_format_name': ''},
                    {'name': (al['asset_method'] == 'linear' and _('Linear')) or (al['asset_method'] == 'degressive' and _('Degressive')) or _('Accelerated'), 'no_format_name': ''},
                    {'name': asset_depreciation_rate, 'no_format_name': ''},
                    {'name': self.format_value(asset_opening), 'no_format_name': asset_opening},  # Assets
                    {'name': self.format_value(asset_add), 'no_format_name': asset_add},
                    {'name': self.format_value(asset_minus), 'no_format_name': asset_minus},
                    {'name': self.format_value(asset_closing), 'no_format_name': asset_closing},
                    {'name': self.format_value(depreciation_opening), 'no_format_name': depreciation_opening},  # Depreciation
                    {'name': self.format_value(depreciation_add), 'no_format_name': depreciation_add},
                    {'name': self.format_value(depreciation_minus), 'no_format_name': depreciation_minus},
                    {'name': self.format_value(depreciation_closing), 'no_format_name': depreciation_closing},
                    {'name': self.format_value(asset_gross), 'no_format_name': asset_gross},  # Gross
                ],
                'unfoldable': False,
                'unfolded': False,
                'caret_options': 'account.asset.line',
                'account_id': al['account_id']
            }
            if len(name) >= MAX_NAME_LENGTH:
                line.update({'title_hover': name})
            lines.append(line)

        correction = self.env['account.asset.correction'].search([
            ('state', '=', 'posted'),
            ('date', '<=', options['date']['date_to'])
        ], order='date')

        for correct in correction:

            asset_model = self.env['account.asset'].search([
                ('state', '=', 'model'),
                ('account_depreciation_id', 'in', [line.account_id.id for line in correct.line_ids]),
                ('account_depreciation_expense_id', 'in', [line.account_id.id for line in correct.line_ids])
            ])

            if asset_model:
                fixed_account_id = asset_model[0].account_asset_id
            else:
                raise UserError(_('Fixed account of asset not found!'))

            account_depreciation_ids = self.env['account.asset.correction.line'].search([
                ('move_id', '=', correct.id),
                ('account_id.user_type_id.name', '=', 'Aset Tetap')
            ])
            correct_amount = 0.0
            for account in account_depreciation_ids:
                correct_amount += account.debit - account.credit

            asset_opening = 0.0
            asset_add = 0.0
            asset_minus = 0.0
            depreciation_opening = 0.0
            depreciation_add = 0.0
            depreciation_minus = 0.0

            if correct_amount > 0:
                asset_add = correct_amount
                depreciation_minus = correct_amount
            else:
                asset_minus = -correct_amount
                depreciation_add = -correct_amount
            asset_closing = asset_opening + asset_add - asset_minus
            depreciation_closing = depreciation_opening + depreciation_add - depreciation_minus
            asset_gross = correct.book_value

            if not correct.is_correct_depreciation:
                depreciation_opening = depreciation_add = depreciation_minus = depreciation_closing = 0.0
            if not correct.is_correct_asset:
                asset_opening = asset_add = asset_minus = asset_closing = 0.0

            values = {
                'id': f'{self._get_account_group(fixed_account_id.code)[0]}_{correct.id}',
                'level': 2,
                'name': f"{correct.ref} ({format_date(self.env, correct.date)})",
                'columns': [
                    {'name': '', 'no_format_name': ''},  # Caracteristics
                    {'name': '', 'no_format_name': ''},
                    {'name': '', 'no_format_name': ''},
                    {'name': '', 'no_format_name': ''},
                    {'name': self.format_value(asset_opening), 'no_format_name': asset_opening},  # Assets
                    {'name': self.format_value(asset_add), 'no_format_name': asset_add},
                    {'name': self.format_value(asset_minus), 'no_format_name': asset_minus},
                    {'name': self.format_value(asset_closing), 'no_format_name': asset_closing},
                    {'name': self.format_value(depreciation_opening), 'no_format_name': depreciation_opening},  # Depreciation
                    {'name': self.format_value(depreciation_add), 'no_format_name': depreciation_add},
                    {'name': self.format_value(depreciation_minus), 'no_format_name': depreciation_minus},
                    {'name': self.format_value(depreciation_closing), 'no_format_name': depreciation_closing},
                    {'name': self.format_value(asset_gross), 'no_format_name': asset_gross},  # Gross
                ],
                'style': 'font-weight: bold;',
                'class': 'text-danger',
                'unfoldable': False,
                'unfolded': False,
                'account_id': fixed_account_id.id,
                'caret_options': 'account.asset.correction',
            }

            total = [x + y for x, y in zip(total, [asset_opening, asset_add, asset_minus, asset_closing, depreciation_opening, depreciation_add, depreciation_minus, depreciation_closing, asset_gross])]

            lines.append(values)

        lines.append({
            'id': 'total',
            'level': 0,
            'name': _('Total'),
            'columns': [
                {'name': ''},  # Caracteristics
                {'name': ''},
                {'name': ''},
                {'name': ''},
                {'name': self.format_value(total[0])},  # Assets
                {'name': self.format_value(total[1])},
                {'name': self.format_value(total[2])},
                {'name': self.format_value(total[3])},
                {'name': self.format_value(total[4])},  # Depreciation
                {'name': self.format_value(total[5])},
                {'name': self.format_value(total[6])},
                {'name': self.format_value(total[7])},
                {'name': self.format_value(total[8])},  # Gross
            ],
            'unfoldable': False,
            'unfolded': False,
        })

        return lines

    def _get_assets_lines(self, options):
        "Get the data from the database"

        self.env['account.move.line'].check_access_rights('read')
        self.env['account.asset'].check_access_rights('read')

        where_account_move = " AND state != 'cancel'"
        if not options.get('all_entries'):
            where_account_move = " AND state = 'posted'"

        sql = """
                -- remove all the moves that have been reversed from the search
                CREATE TEMPORARY TABLE IF NOT EXISTS temp_account_move () INHERITS (account_move) ON COMMIT DROP;
                INSERT INTO temp_account_move SELECT move.*
                FROM ONLY account_move move
                LEFT JOIN ONLY account_move reversal ON reversal.reversed_entry_id = move.id
                WHERE reversal.id IS NULL AND move.asset_id IS NOT NULL AND move.company_id in %(company_ids)s;

                SELECT asset.id as asset_id,
                       asset.parent_id as parent_id,
                       asset.name as asset_name,
                       asset.value_residual as asset_value,
                       asset.original_value as asset_original_value,
                       asset.first_depreciation_date as asset_date,
                       asset.disposal_date as asset_disposal_date,
                       asset.acquisition_date as asset_acquisition_date,
                       asset.method as asset_method,
                       (
                           (SELECT COUNT(*) FROM temp_account_move WHERE asset_id = asset.id AND asset_value_change != 't')
                           - CASE WHEN asset.prorata THEN 1 ELSE 0 END
                       ) as asset_method_number,
                       asset.method_period as asset_method_period,
                       asset.method_progress_factor as asset_method_progress_factor,
                       asset.state as asset_state,
                       account.code as account_code,
                       account.name as account_name,
                       account.id as account_id,
                       COALESCE(first_move.asset_depreciated_value, move_before.asset_depreciated_value, 0.0) as depreciated_start,
                       COALESCE(first_move.asset_remaining_value, move_before.asset_remaining_value, 0.0) as remaining_start,
                       COALESCE(last_move.asset_depreciated_value, move_before.asset_depreciated_value, 0.0) as depreciated_end,
                       COALESCE(last_move.asset_remaining_value, move_before.asset_remaining_value, 0.0) as remaining_end,
                       COALESCE(first_move.amount_total, 0.0) as depreciation
                FROM account_asset as asset
                LEFT JOIN account_account as account ON asset.account_asset_id = account.id
                LEFT OUTER JOIN (SELECT MIN(date) as date, asset_id FROM temp_account_move WHERE date >= %(date_from)s AND date <= %(date_to)s {where_account_move} GROUP BY asset_id) min_date_in ON min_date_in.asset_id = asset.id
                LEFT OUTER JOIN (SELECT MAX(date) as date, asset_id FROM temp_account_move WHERE date >= %(date_from)s AND date <= %(date_to)s {where_account_move} GROUP BY asset_id) max_date_in ON max_date_in.asset_id = asset.id
                LEFT OUTER JOIN (SELECT MAX(date) as date, asset_id FROM temp_account_move WHERE date <= %(date_from)s {where_account_move} GROUP BY asset_id) max_date_before ON max_date_before.asset_id = asset.id
                LEFT OUTER JOIN temp_account_move as first_move ON first_move.id = (SELECT m.id FROM temp_account_move m WHERE m.asset_id = asset.id AND m.date = min_date_in.date ORDER BY m.id ASC LIMIT 1)
                LEFT OUTER JOIN temp_account_move as last_move ON last_move.id = (SELECT m.id FROM temp_account_move m WHERE m.asset_id = asset.id AND m.date = max_date_in.date ORDER BY m.id DESC LIMIT 1)
                LEFT OUTER JOIN temp_account_move as move_before ON move_before.id = (SELECT m.id FROM temp_account_move m WHERE m.asset_id = asset.id AND m.date = max_date_before.date ORDER BY m.id DESC LIMIT 1)
                WHERE asset.company_id in %(company_ids)s
                AND asset.acquisition_date <= %(date_to)s
                AND (asset.disposal_date >= %(date_from)s OR asset.disposal_date IS NULL)
                AND asset.state not in ('model', 'draft')
                AND asset.asset_type = 'purchase'
                AND asset.active = 't'

                ORDER BY asset.first_depreciation_date;
            """.format(where_account_move=where_account_move)

        date_to = options['date']['date_to']
        date_from = options['date']['date_from']
        company_ids = tuple(t['id'] for t in self._get_options_companies(options))

        self.flush()
        self.env.cr.execute(sql, {'date_to': date_to, 'date_from': date_from, 'company_ids': company_ids})
        results = self.env.cr.dictfetchall()
        self.env.cr.execute("DROP TABLE temp_account_move")  # Because tests are run in the same transaction, we need to clean here the SQL INHERITS
        return results

