from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    project_name = fields.Char(string='Project Name')
