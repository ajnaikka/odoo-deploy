# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerRequiredFields(http.Controller):
#     @http.route('/partner_required_fields/partner_required_fields', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_required_fields/partner_required_fields/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_required_fields.listing', {
#             'root': '/partner_required_fields/partner_required_fields',
#             'objects': http.request.env['partner_required_fields.partner_required_fields'].search([]),
#         })

#     @http.route('/partner_required_fields/partner_required_fields/objects/<model("partner_required_fields.partner_required_fields"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_required_fields.object', {
#             'object': obj
#         })
