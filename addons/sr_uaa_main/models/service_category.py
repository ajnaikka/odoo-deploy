from odoo import models, fields, api, _


class ServiceCategory(models.Model):
    _name = 'service.category'
    _description = 'Services Category provided at Airports'
    _order = 'sequence'

    _sql_constraints = [
        ('unique_service_name', 'UNIQUE (name)', 'Service Name must be unique!'),
    ]

    sequence = fields.Integer()
    name = fields.Char('Name', required=True)
    description = fields.Html('Description')
    product_id = fields.Many2one('product.template', 'Product')

    @api.model
    def create(self, vals_list):
        product_id = False
        if vals_list.get('name'):
            product_env = self.env['product.template'].sudo()
            vals = {
                'name': vals_list.get('name'),
                'type': 'service',
                'invoice_policy': 'order',
                'list_price': 0,
            }
            product_id = product_env.create(vals)
            vals_list.update({
                'product_id': product_id and product_id.id or False,
            })
        res = super(ServiceCategory, self).create(vals_list)
        if product_id:
            product_id.service_category_id = res.id
            product_id.description = res.description
        return res

    def write(self, vals):
        if vals:
            product_vals = {
                'service_category_id': self.id,
            }
            if vals.get('description'):
                product_vals.update({
                    'description': vals.get('description'),
                })
            if vals.get('name'):
                product_vals.update({
                    'name': vals.get('name'),
                })
            if self.product_id:
                self.product_id.write(product_vals)
            else:
                if not product_vals.get('name'):
                    product_vals.update({
                        'name': self.name or ''
                    })
                product_env = self.env['product.template'].sudo()
                product_vals.update({
                    'type': 'service',
                    'invoice_policy': 'order',
                    'service_category_id': self.id,
                })
                product_id = product_env.create(product_vals)
                vals.update({
                    'product_id': product_id and product_id.id or False,
                })
        res = super(ServiceCategory, self).write(vals)
        return res
