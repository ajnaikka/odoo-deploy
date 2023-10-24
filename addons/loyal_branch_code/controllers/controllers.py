# -*- coding: utf-8 -*-
# from odoo import http


# class LoyalBranchCode(http.Controller):
#     @http.route('/loyal_branch_code/loyal_branch_code', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loyal_branch_code/loyal_branch_code/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('loyal_branch_code.listing', {
#             'root': '/loyal_branch_code/loyal_branch_code',
#             'objects': http.request.env['loyal_branch_code.loyal_branch_code'].search([]),
#         })

#     @http.route('/loyal_branch_code/loyal_branch_code/objects/<model("loyal_branch_code.loyal_branch_code"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loyal_branch_code.object', {
#             'object': obj
#         })
