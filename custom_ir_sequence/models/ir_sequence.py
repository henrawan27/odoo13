from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import calendar
import pytz


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    reset_range = fields.Selection(
        selection=[('month', 'Per Month'), ('year', 'Per Year')],
        string='Reset Method',
        required=True,
        default='year'
    )

    @api.model
    def change_format(self):
        journals = self.env['account.journal'].search([])
        for journal in journals:
            journal.sequence_id.prefix = journal.code + '/%(roman_month)s/%(range_year)s/'

    def _create_date_range_seq(self, date):
        if self.reset_range == 'year':
            return super(IrSequence, self)._create_date_range_seq(date)

        month = fields.Date.from_string(date).strftime('%Y-%m')
        end_of_month = calendar.monthrange(date.year, date.month)[1]
        date_from = '{}-01'.format(month)
        date_to = '{}-{}'.format(month, end_of_month)
        date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id), ('date_from', '>=', date), ('date_from', '<=', date_to)], order='date_from desc', limit=1)
        if date_range:
            date_to = date_range.date_from + timedelta(days=-1)
        date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id), ('date_to', '>=', date_from), ('date_to', '<=', date)], order='date_to desc', limit=1)
        if date_range:
            date_from = date_range.date_to + timedelta(days=1)
        seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
            'date_from': date_from,
            'date_to': date_to,
            'sequence_id': self.id,
        })
        return seq_date_range

    def _get_prefix_suffix(self, date=None, date_range=None):
        def _interpolate(s, d):
            return (s % d) if s else ''

        def int_to_roman(num):
            val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
            syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
            roman_num = ''
            i = 0
            while num > 0:
                for j in range(num // val[i]):
                    roman_num += syb[i]
                    num -= val[i]
                i += 1
            return roman_num

        def _interpolation_dict():
            now = range_date = effective_date = datetime.now(pytz.timezone(self._context.get('tz') or 'UTC'))
            if date or self._context.get('ir_sequence_date'):
                effective_date = fields.Datetime.from_string(date or self._context.get('ir_sequence_date'))
            if date_range or self._context.get('ir_sequence_date_range'):
                range_date = fields.Datetime.from_string(date_range or self._context.get('ir_sequence_date_range'))

            sequences = {
                'year': '%Y', 'month': '%m', 'day': '%d', 'y': '%y', 'doy': '%j', 'woy': '%W',
                'weekday': '%w', 'h24': '%H', 'h12': '%I', 'min': '%M', 'sec': '%S'
            }
            res = {}
            for key, form in sequences.items():
                res[key] = effective_date.strftime(form)
                res['range_' + key] = range_date.strftime(form)
                res['current_' + key] = now.strftime(form)

                # add roman values
                res['roman_' + key] = int_to_roman(int(res[key]))
                res['range_roman_' + key] = int_to_roman(int(res['range_' + key]))
                res['current_roman_' + key] = int_to_roman(int(res['current_' + key]))

            return res

        d = _interpolation_dict()
        try:
            interpolated_prefix = _interpolate(self.prefix, d)
            interpolated_suffix = _interpolate(self.suffix, d)
        except ValueError:
            raise UserError(_('Invalid prefix or suffix for sequence \'%s\'') % (self.get('name')))
        return interpolated_prefix, interpolated_suffix
