from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HRExpenseSheet(models.Model):
	_inherit = "hr.expense.sheet"

	sale_id = fields.Many2one('sale.order', string='Sale Order')
	sale_partner_id = fields.Many2one('res.partner', related='sale_id.partner_id')
	
	@api.onchange('sale_id', 'employee_id')
	def _onchange_sale_employee(self):
		domain = [
			('sale_id', '=', self.sale_id.id),
			('state', '=', 'draft'),
			('employee_id', '=', self.employee_id.id),
			('company_id', '=', self.company_id.id)
		]
		expense_ids = self.env['hr.expense'].search(domain)
		self.expense_line_ids = [(6, 0, expense_ids.ids)]

	@api.constrains('expense_line_ids')
	def _check_expense_line_ids(self):
		sale_ids = self.expense_line_ids.mapped('sale_id')
		if len(sale_ids) == 1:
			if sale_ids[0].sale_id != self.sale_id:
				raise ValidationError(_("Expenses sale order must be same with Report sale order"))
		elif len(sale_ids) > 1:
			raise ValidationError(_("Can't add expenses that has different sale order"))
