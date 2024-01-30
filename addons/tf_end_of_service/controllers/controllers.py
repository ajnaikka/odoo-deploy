# -*- coding: utf-8 -*-
# from odoo import http


# class TfEndOfService(http.Controller):
#     @http.route('/tf_end_of_service/tf_end_of_service', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tf_end_of_service/tf_end_of_service/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tf_end_of_service.listing', {
#             'root': '/tf_end_of_service/tf_end_of_service',
#             'objects': http.request.env['tf_end_of_service.tf_end_of_service'].search([]),
#         })

#     @http.route('/tf_end_of_service/tf_end_of_service/objects/<model("tf_end_of_service.tf_end_of_service"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tf_end_of_service.object', {
#             'object': obj
#         })

