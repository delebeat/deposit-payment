# -*- coding: utf-8 -*-
# from odoo import http


# class DelPaymentApprovalCashier(http.Controller):
#     @http.route('/del_payment_approval_cashier/del_payment_approval_cashier', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/del_payment_approval_cashier/del_payment_approval_cashier/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('del_payment_approval_cashier.listing', {
#             'root': '/del_payment_approval_cashier/del_payment_approval_cashier',
#             'objects': http.request.env['del_payment_approval_cashier.del_payment_approval_cashier'].search([]),
#         })

#     @http.route('/del_payment_approval_cashier/del_payment_approval_cashier/objects/<model("del_payment_approval_cashier.del_payment_approval_cashier"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('del_payment_approval_cashier.object', {
#             'object': obj
#         })
