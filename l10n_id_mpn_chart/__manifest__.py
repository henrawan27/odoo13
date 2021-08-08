# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'MPN Chart Template',
    'version': '13.0.1',
    'category': 'Localization',
    'author': 'Rajib Deyana, DSI Bandung',
    'summary': "MPN Chart Template",
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'depends': ['account', 'base_iban', 'base_vat', 'l10n_generic_coa'],
    'license': 'LGPL-3',
    'data': [
        'data/account_account_type_data.xml',
        'data/account_chart_template_data.xml',
        'data/account.account.template.csv',
        'data/account_chart_template_post_data.xml',
        'data/account_chart_template_configuration_data.xml',
        'views/account_reconcile_model_views.xml',
    ]
}
