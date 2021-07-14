from odoo import models, tools


class Website(models.Model):
    _inherit = 'website'

    @tools.ormcache('self.env.uid', 'self.id')
    def _get_menu_ids(self):
        menu_ids = super(Website, self)._get_menu_ids()
        menus = self.env['website.menu'].browse(menu_ids)

        for menu in menus:
            if not self.env.user.employee_id and menu.only_employee:
                menu_ids.remove(menu.id)
        return menu_ids
