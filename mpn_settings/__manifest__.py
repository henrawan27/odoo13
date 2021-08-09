# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'MPN Settings',
    'version': '13.0.1',
    'category': 'Accounting',
    'summary': "Extra setting for MPN",
    'author': 'Rajib Deyana, DSI Bandung',
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'account_accountant',
        'custom_account_move',
        'custom_ir_sequence',
        'custom_account_asset',
        'custom_account_payment',
        'custom_account_reports',
        'financial_report',
    ],
    'data': [
        'data/company_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
