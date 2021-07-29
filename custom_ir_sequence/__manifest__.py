# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Ir Sequence',
    'version': '13.0.1',
    'category': 'Accounting',
    'summary': "Custom sequence numbering for MPN",
    'author': 'Rajib Deyana, DSI Bandung',
    'website': 'https://www.dwidasa.com',
    'email': 'community@dwidasa.com',
    'license': 'LGPL-3',
    'depends': [
        'account',
    ],
    'data': [
        'views/ir_sequence_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
