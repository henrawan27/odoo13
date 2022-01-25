from odoo import api, fields, models, _
from datetime import date, timedelta

class ReportAccountFinancialReport(models.Model):
    _inherit = "account.financial.html.report"

    def _get_columns_name(self, options):
        columns = [{'name': ''}]
        if self.debit_credit and not options.get('comparison', {}).get('periods', False):
            columns += [{'name': _('Debit'), 'class': 'number'}, {'name': _('Credit'), 'class': 'number'}]
        if not self.filter_date:
            if self.date_range:
                self.filter_date = {'mode': 'range', 'filter': 'this_year'}
            else:
                self.filter_date = {'mode': 'single', 'filter': 'today'}
        columns += [{'name': self.format_date(options), 'class': 'number'}]
        if options.get('comparison') and options['comparison'].get('periods'):
            # v_periods = options['comparison']['periods']
            # v_periods.reverse()
            for period in options['comparison']['periods']:                
                columns += [{'name': period.get('string'), 'class': 'number'}]
            if options['comparison'].get('number_period') == 1 and not options.get('groups'):
                columns += [{'name': '%', 'class': 'number'}]

        if options.get('groups', {}).get('ids'):
            columns_for_groups = []
            for column in columns[1:]:
                for ids in options['groups'].get('ids'):
                    group_column_name = ''
                    for index, id in enumerate(ids):
                        column_name = self._get_column_name(id, options['groups']['fields'][index])
                        group_column_name += ' ' + column_name
                    columns_for_groups.append({'name': column.get('name') + group_column_name, 'class': 'number'})
            columns = columns[:1] + columns_for_groups

        v_columns = []
        columns.reverse()
        for i in columns:
            if i['name'] == '':
                continue
            else:
                v_columns.append(i)

        v_columns.insert(0, {'name': ''})

        # return columns
        return v_columns

    def _get_lines(self, options, line_id=None):
        line_obj = self.line_ids
        if line_id:
            line_obj = self.env['account.financial.html.report.line'].search([('id', '=', line_id)])
        if options.get('comparison') and options.get('comparison').get('periods'):
            line_obj = line_obj.with_context(periods=options['comparison']['periods'])
        if options.get('ir_filters'):
            line_obj = line_obj.with_context(periods=options.get('ir_filters'))

        currency_table = self._get_currency_table()
        domain, group_by = self._get_filter_info(options)

        if group_by:
            options['groups'] = {}
            options['groups']['fields'] = group_by
            options['groups']['ids'] = self._get_groups(domain, group_by)

        amount_of_periods = len((options.get('comparison') or {}).get('periods') or []) + 1
        amount_of_group_ids = len(options.get('groups', {}).get('ids') or []) or 1
        linesDicts = [[{} for _ in range(0, amount_of_group_ids)] for _ in range(0, amount_of_periods)]

        res = line_obj.with_context(
            filter_domain=domain,
        )._get_lines(self, currency_table, options, linesDicts)

        for res_v in res:
            v_columns = res_v['columns']
            v_columns.reverse()

        return res