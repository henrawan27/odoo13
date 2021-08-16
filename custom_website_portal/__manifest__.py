# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Website Portal',
    'version': '13.0.1',
    'category': 'Website',
    'author': 'Rajib Deyana, DSI Bandung',
    'summary': "Odoo 13 Custom Website Portal",
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'depends': [
        'web',
        'website',
        'portal',
        'sale',
        'sale_management',
        'hr',
        'hr_expense',
    ],
    'license': 'LGPL-3',
    'data': [
        'templates/webclient_templates.xml',
        'templates/layout_templates.xml',
        'templates/view_templates.xml',
        'templates/modal_templates.xml',

        'views/hr_expense_views.xml',
        'views/hr_expense_sheet_views.xml',
        'views/sale_views.xml',

        'views/hr_expense_form.xml',
        'views/hr_employee_form.xml',

        'views/website_form.xml',
    ],
    "images": [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
