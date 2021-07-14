# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'MPN Accounting',
    'version': '13.0.1',
    'category': 'Accounting',
    'summary': "Custom accounting setting for MPN",
    'author': 'Rajib Deyana, DSI Bandung',
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'account_accountant',
        'l10n_id_efaktur',
        'mpn_chart_template_fix',
        'custom_account_move',
        'custom_account_asset',
        'custom_account_payment',
        'custom_account_reports',
        'custom_website_portal',
        'financial_report',
    ],
    'data': [
        'data/account_tax_data.xml',
        'data/financial_report_data.xml',
        'data/company_settings.xml',
        'views/account_move_filters.xml',
        'views/ir_sequence_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
