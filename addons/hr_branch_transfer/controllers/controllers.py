# -*- coding: utf-8 -*-
# from odoo import http


# class HrBranchTransfer(http.Controller):
#     @http.route('/hr_branch_transfer/hr_branch_transfer', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hr_branch_transfer/hr_branch_transfer/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hr_branch_transfer.listing', {
#             'root': '/hr_branch_transfer/hr_branch_transfer',
#             'objects': http.request.env['hr_branch_transfer.hr_branch_transfer'].search([]),
#         })

#     @http.route('/hr_branch_transfer/hr_branch_transfer/objects/<model("hr_branch_transfer.hr_branch_transfer"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hr_branch_transfer.object', {
#             'object': obj
#         })
