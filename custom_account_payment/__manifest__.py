# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Account Payment',
    'version': '13.0.1',
    'category': 'Accounting',
    'author': 'Rajib Deyana, DSI Bandung',
    'description': "Odoo 13 Custom Account Paymnet",
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'depends': ['account', 'account_reports'],
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'views/account_tax_views.xml',
        'views/account_payment_action.xml',
        'views/account_payment_views.xml',
        'views/account_move_action.xml',
        'views/res_config_settings_views.xml'
    ],
    "images": [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
