# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Account Move',
    'version': '13.0',
    'author': 'Rajib Deyana, DSI Bandung',
    'catgeory': 'Accounting',
    'summary': 'Upload opening balance and auto reconcile opening moves',
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'depends': ['account'],
    'license': 'LGPL-3',
    'data': [
        'views/account_move_views.xml',
        'views/account_auto_reconciliation_views.xml'
    ],
    "images": [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
