# -*- coding: utf-8 -*-
# from odoo import http


# class ProductExpiryNotification(http.Controller):
#     @http.route('/product_expiry_notification/product_expiry_notification', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_expiry_notification/product_expiry_notification/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_expiry_notification.listing', {
#             'root': '/product_expiry_notification/product_expiry_notification',
#             'objects': http.request.env['product_expiry_notification.product_expiry_notification'].search([]),
#         })

#     @http.route('/product_expiry_notification/product_expiry_notification/objects/<model("product_expiry_notification.product_expiry_notification"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_expiry_notification.object', {
#             'object': obj
#         })
