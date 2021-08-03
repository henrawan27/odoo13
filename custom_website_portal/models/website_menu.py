from odoo import models, fields


class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    only_employee = fields.Boolean(string='Menu for Employee Only', default=False)
