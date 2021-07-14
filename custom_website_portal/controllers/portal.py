from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request, route


class CustomerPortal(CustomerPortal):

    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        if not request.env.user.employee_id:
            return super(CustomerPortal, self).home()
        return request.redirect('/portal/home')
