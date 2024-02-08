# -*- coding: utf-8 -*-
# from odoo import http


# class TfEosDueToDeath(http.Controller):
#     @http.route('/tf_eos_due_to_death/tf_eos_due_to_death', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tf_eos_due_to_death/tf_eos_due_to_death/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('tf_eos_due_to_death.listing', {
#             'root': '/tf_eos_due_to_death/tf_eos_due_to_death',
#             'objects': http.request.env['tf_eos_due_to_death.tf_eos_due_to_death'].search([]),
#         })

#     @http.route('/tf_eos_due_to_death/tf_eos_due_to_death/objects/<model("tf_eos_due_to_death.tf_eos_due_to_death"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tf_eos_due_to_death.object', {
#             'object': obj
#         })

