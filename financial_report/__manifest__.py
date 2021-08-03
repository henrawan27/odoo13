# -*- coding: utf-8 -*-
{
    'name': "financial_report",

    'summary': """""",

    'description': """""",

    'author': "DSI",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/financial_views.xml',
        'views/templates.xml',
        # 'data/type_report.xml',
    ],
}
