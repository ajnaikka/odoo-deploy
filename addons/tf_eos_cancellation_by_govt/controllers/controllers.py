# -*- coding: utf-8 -*-
# from odoo import http


# class TfEosCancellationByGovt(http.Controller):
#     @http.route('/tf_eos_cancellation_by_govt/tf_eos_cancellation_by_govt', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tf_eos_cancellation_by_govt/tf_eos_cancellation_by_govt/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tf_eos_cancellation_by_govt.listing', {
#             'root': '/tf_eos_cancellation_by_govt/tf_eos_cancellation_by_govt',
#             'objects': http.request.env['tf_eos_cancellation_by_govt.tf_eos_cancellation_by_govt'].search([]),
#         })

#     @http.route('/tf_eos_cancellation_by_govt/tf_eos_cancellation_by_govt/objects/<model("tf_eos_cancellation_by_govt.tf_eos_cancellation_by_govt"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tf_eos_cancellation_by_govt.object', {
#             'object': obj
#         })

