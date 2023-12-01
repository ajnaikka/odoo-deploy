from odoo import models, fields, api, _
from odoo.osv import expression


class ServiceTypeNames(models.Model):
    _name = 'airport.service.type'
    _description = 'Types of Service provided at Airports'

    name = fields.Char('Name', required=True)
    is_arrival = fields.Boolean('Is Arrival Service', default=False)
    is_departure = fields.Boolean('Is Departure Service', default=False)
    is_transit = fields.Boolean('Is Transit Service', default=False)

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        service_id = self._context.get('service_type_id', False)
        args = args or []
        domain = [('name', operator, name)]
        if service_id:
            service_id = self.env['uaa.services'].sudo().browse(service_id)
            if service_id and service_id.service_type_ids:
                domain = [('id', 'in', service_id.service_type_ids.ids), ('name', operator, name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)


class UaaServices(models.Model):
    _name = 'uaa.services'
    _description = 'Services provided by UAA'

    name = fields.Char('Name', required=True)
    url = fields.Char('Website URL', required=True, readonly=True)
    service_type_ids = fields.Many2many('airport.service.type','uaa_service_type_rel','service_id','type_id','Service Type')