# -*- coding: utf-8 -*-
from odoo import models, fields, api
# from random import choice
# from string import digits

class ProductProduct(models.Model):
    _inherit = "product.product"
#
#     # def generate_random_barcode(self):
#     #     for employee in self:
#     #         employee.barcode = '041'+"".join(choice(digits) for i in range(9))

    @api.model
    def create(self, vals):
        res = super(ProductProduct, self).create(vals)
        if not vals.get('barcode'):
            number = self.env['ir.sequence'].next_by_code('product.barcode.sequence')
            res.barcode = number
            # res['barcode'] = self.env['ir.sequence'].next_by_code('product.barcode.sequence')
        return res
    # @api.model
    # def create(self, vals):
    #     res = super(ProductProduct, self).create(vals)
    #     if 'barcode' not in vals:
    #         number = self.env['ir.sequence'].next_by_code('product.barcode.sequence') or 'New'
    #         res.barcode = number
    #     return res


#
# class ProductTemplate(models.Model):
#     _inherit = 'product.template'
#
#     @api.model
#     def create(self, vals_list):
#         res = super(ProductTemplate, self).create(vals_list)
#         if 'barcode' not in vals_list:
#             number = self.env['ir.sequence'].next_by_code('template.barcode.sequence') or 'New'
#             res.barcode = number
#         return res