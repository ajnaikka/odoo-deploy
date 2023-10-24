# -*- coding: utf-8 -*-
# from odoo import http


# class ProductBarcodeSequence(http.Controller):
#     @http.route('/product_barcode_sequence/product_barcode_sequence/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_barcode_sequence/product_barcode_sequence/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_barcode_sequence.listing', {
#             'root': '/product_barcode_sequence/product_barcode_sequence',
#             'objects': http.request.env['product_barcode_sequence.product_barcode_sequence'].search([]),
#         })

#     @http.route('/product_barcode_sequence/product_barcode_sequence/objects/<model("product_barcode_sequence.product_barcode_sequence"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_barcode_sequence.object', {
#             'object': obj
#         })
