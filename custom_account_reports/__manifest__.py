# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Account Reports',
    'version': '13.0.1',
    'category': 'Accounting',
    'author': 'Rajib Deyana, DSI Bandung',
    'summary': "Odoo 13 Custom Account Reports",
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'depends': [
        'account_reports',
        'custom_account_asset'
    ],
    'license': 'LGPL-3',
    'data': [
        'data/financial_report_data.xml',
        'views/search_template_views.xml',
        'views/res_config_settings_views.xml'
    ],
    "images": [],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
