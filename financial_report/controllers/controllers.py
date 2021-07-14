# -*- coding: utf-8 -*-
# from odoo import http


# class FinancialReport(http.Controller):
#     @http.route('/financial_report/financial_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/financial_report/financial_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('financial_report.listing', {
#             'root': '/financial_report/financial_report',
#             'objects': http.request.env['financial_report.financial_report'].search([]),
#         })

#     @http.route('/financial_report/financial_report/objects/<model("financial_report.financial_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('financial_report.object', {
#             'object': obj
#         })
