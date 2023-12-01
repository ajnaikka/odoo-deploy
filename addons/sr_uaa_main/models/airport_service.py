from odoo import models, fields, api, _


class ServiceNames(models.Model):
    _name = 'airport.service.name'
    _description = 'Services provided at Airports'

    name = fields.Char('Name', required=True)
    service_charge = fields.Float('Service Charge', default="0.00")
    show_meet_greet = fields.Boolean('Show in Meet and Greet')


class ServiceLine(models.Model):
    _name = 'service.line'
    _description = 'Service Line'

    airport_id = fields.Many2one('admin.airport', string='Airport Details')
    services = fields.Selection([('meet_assist', 'Meet & Assist'),
                                 ('airport_hotel', 'Airport Hotel'),
                                 ('airport_lounge', 'Airport Lounge'),
                                 ('airport_transfer', 'Airport Transfer')
                                 ], string='Service', compute='get_uaa_services', store=True)
    service_type = fields.Selection([('arrival', 'Arrival Service'),
                                     ('departure', 'Departure Service'),
                                     ('transit', 'Transit Service')],
                                    string='Service Type', compute="get_service_type", store=True)
    service_type_id = fields.Many2one('airport.service.type', 'Service Type')
    uaa_services_id = fields.Many2one('uaa.services', 'Service')
    price_text = fields.Text('Service Charge', compute="compute_service_charge", store=True)
    services_ids = fields.One2many('airport.service.line','service_id', string="services")

    @api.depends('uaa_services_id')
    def get_uaa_services(self):
        for rec in self:
            rec.services = False
            if rec.uaa_services_id:
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.meet_greet_services"):
                    rec.services = 'meet_assist'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_hotel_services"):
                    rec.services = 'airport_hotel'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_lounge_services"):
                    rec.services = 'airport_lounge'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                    rec.services = 'airport_transfer'

    @api.depends('service_type_id')
    def get_service_type(self):
        for rec in self:
            rec.service_type = False
            if rec.service_type_id:
                if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    rec.service_type = 'arrival'
                if rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    rec.service_type = 'departure'
                if rec.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    rec.service_type = 'transit'

    def update_services(self):
        for rec in self:
            form_view_id = self.env.ref('sr_uaa_main.view_service_airport_pricelist_form').id
            tree_view_id = self.env.ref('sr_uaa_main.view_service_airport_pricelist_tree').id
            context = self._context.copy()
            context.update({
                'default_airport_id': rec.airport_id and rec.airport_id.id or False,
                'default_services': rec.services or False,
                'default_uaa_services_id': rec.uaa_services_id and rec.uaa_services_id.id or False,
                'default_service_type': rec.service_type or False,
                'default_service_type_id': rec.service_type_id and rec.service_type_id.id or False,
                'default_service_id': rec.id,
            })
            return {
                'name':'Service',
                'view_mode': 'tree,form',
                'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
                'res_model': 'airport.service.line',
                'view_id': tree_view_id,
                'type': 'ir.actions.act_window',
                'domain': [('service_id','=',rec.id)],
                'context': context,
            }


    @api.depends('services_ids','services_ids.service_category_id',
                 'services_ids.service_category_id.name',
                 'services_ids.service_type','services_ids.airport_id',
                 'services_ids.services','services_ids.amount')
    def compute_service_charge(self):
        for rec in self:
            price_text = ''
            for service in rec.services_ids:
                if price_text:
                    price_text += ', \n'
                if service.service_category_id:
                    price_text += service.service_category_id.name
                    price_text += ' = '
                    price_text += str(service.amount)
            if price_text:
                price_text += '.'
            rec.price_text = price_text

class AirportServiceLine(models.Model):
    _name = 'airport.service.line'
    _description = 'Airport Service Line'
    _rec_name = 'service_category_id'

    airport_id = fields.Many2one('admin.airport', string='Airport Details')
    service_category_id = fields.Many2one('service.category', string='Service Category')
    description = fields.Html('Description')
    service_id = fields.Many2one('service.line', string='Services')
    services = fields.Selection([('meet_assist', 'Meet & Assist'),
                                 ('airport_hotel', 'Airport Hotel'),
                                 ('airport_lounge', 'Airport Lounge'),
                                 ('airport_transfer', 'Airport Transfer')
                                 ], string='Service', compute='get_uaa_services', store=True)
    service_type = fields.Selection([('arrival', 'Arrival Service'),
                                     ('departure', 'Departure Service'),
                                     ('transit', 'Transit Service')],
                                    string='Service Type', compute="get_service_type", store=True)
    service_type_id = fields.Many2one('airport.service.type', 'Service Type')
    uaa_services_id = fields.Many2one('uaa.services', 'Service')
    amount = fields.Float(string='Amount', default=0.0)

    @api.depends('uaa_services_id')
    def get_uaa_services(self):
        for rec in self:
            rec.services = False
            if rec.uaa_services_id:
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.meet_greet_services"):
                    rec.services = 'meet_assist'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_hotel_services"):
                    rec.services = 'airport_hotel'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_lounge_services"):
                    rec.services = 'airport_lounge'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                    rec.services = 'airport_transfer'

    @api.depends('service_type_id')
    def get_service_type(self):
        for rec in self:
            rec.service_type = False
            if rec.service_type_id:
                if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    rec.service_type = 'arrival'
                if rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    rec.service_type = 'departure'
                if rec.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    rec.service_type = 'transit'

    @api.model
    def default_get(self, fields_list):
        res = super(AirportServiceLine, self).default_get(fields_list)

        airport_id = False
        if self._context.get('default_enquiry_id', False):
            enquiry_id = self.env['airport.enquiry'].sudo().browse(self._context.get('default_enquiry_id'))
            if enquiry_id:
                if enquiry_id.service_type_id and enquiry_id.uaa_services_id:
                    if enquiry_id.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                        if enquiry_id.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                            airport_id = enquiry_id.pick_up_airport_id and enquiry_id.pick_up_airport_id.id or False
                        elif enquiry_id.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                            airport_id = enquiry_id.drop_off_airport_id and enquiry_id.drop_off_airport_id.id or False
                    else:
                        airport_id = enquiry_id.airport_id and enquiry_id.airport_id.id or False

            res['airport_id'] = airport_id

        return res

    @api.model
    def create(self, vals_list):
        if vals_list.get('service_category_id'):
            if not vals_list.get('description'):
                service_category_id = self.env['service.category'].sudo().browse(int(vals_list.get('service_category_id')))
                if service_category_id:
                    vals_list.update({
                        'description': service_category_id.description
                    })
        res = super(AirportServiceLine, self).create(vals_list)
        return res

    def write(self, vals):
        if vals.get('service_category_id'):
            if not vals.get('description'):
                service_category_id = self.env['service.category'].sudo().browse(
                    int(vals.get('service_category_id')))
                if service_category_id:
                    vals.update({
                        'description': service_category_id.description
                    })
        res = super(AirportServiceLine, self).write(vals)
        return res

    @api.onchange('service_category_id')
    def onchange_service_category_id(self):
        for rec in self:
            description = False
            if rec.service_category_id:
                description = rec.service_category_id.description
            rec.description = description

class EnquiryServiceLine(models.Model):
    _name = 'enquiry.service.line'
    _rec_name = 'combination'

    @api.depends('uaa_services_id')
    def get_uaa_services(self):
        for rec in self:
            rec.services = False
            if rec.uaa_services_id:
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.meet_greet_services"):
                    rec.services = 'meet_assist'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_hotel_services"):
                    rec.services = 'airport_hotel'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_lounge_services"):
                    rec.services = 'airport_lounge'
                if rec.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                    rec.services = 'airport_transfer'

    @api.depends('service_type_id')
    def get_service_type(self):
        for rec in self:
            rec.service_type = False
            if rec.service_type_id:
                if rec.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                    rec.service_type = 'arrival'
                if rec.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                    rec.service_type = 'departure'
                if rec.service_type_id == self.env.ref("sr_uaa_main.transit_service_type"):
                    rec.service_type = 'transit'

    @api.depends('service_category_id', 'service_type_id',
                 'service_category_id.name','uaa_services_id',
                 'uaa_services_id.name', 'service_type_id.name')
    def _compute_fields_combination(self):
        for rec in self:
            rec.combination = (rec.uaa_services_id and rec.uaa_services_id.name or '')+\
                              ' ' + (rec.service_type_id and rec.service_type_id.name or '') +\
                              ' ' + (rec.service_category_id and rec.service_category_id.name or '' )

    airport_id = fields.Many2one('admin.airport', string='Airport Details')
    combination = fields.Char(string='Combination', compute='_compute_fields_combination', store=True)
    service_category_id = fields.Many2one('service.category', string='Service Category')
    description = fields.Html('Description')
    services = fields.Selection([('meet_assist', 'Meet & Assist'),
                                 ('airport_hotel', 'Airport Hotel'),
                                 ('airport_lounge', 'Airport Lounge'),
                                 ('airport_transfer', 'Airport Transfer')
                                 ], string='Service', compute='get_uaa_services', store=True)
    service_type = fields.Selection([('arrival', 'Arrival Service'),
                                     ('departure', 'Departure Service'),
                                     ('transit', 'Transit Service')],
                                    string='Service Type', compute="get_service_type", store=True)
    service_type_id = fields.Many2one('airport.service.type', 'Service Type')
    uaa_services_id = fields.Many2one('uaa.services', 'Service')
    amount = fields.Float(string='Amount', default=0.0)
    enquiry_id = fields.Many2one('airport.enquiry', 'Enquiry')

    @api.model
    def create(self, vals_list):
        if vals_list.get('service_category_id'):
            if not vals_list.get('description'):
                service_category_id = self.env['service.category'].sudo().browse(int(vals_list.get('service_category_id')))
                if service_category_id:
                    vals_list.update({
                        'description': service_category_id.description
                    })

        res = super(EnquiryServiceLine, self).create(vals_list)
        return res

    @api.onchange('service_category_id')
    def onchange_service_category_id(self):
        for rec in self:
            description = False
            if rec.service_category_id:
                description = rec.service_category_id.description
            rec.description = description

    def write(self, vals):
        if vals.get('service_category_id'):
            if not vals.get('description'):
                service_category_id = self.env['service.category'].sudo().browse(
                    int(vals.get('service_category_id')))
                if service_category_id:
                    vals.update({
                        'description': service_category_id.description
                    })
        res = super(EnquiryServiceLine, self).write(vals)
        return res

    @api.model
    def default_get(self, fields_list):
        res = super(EnquiryServiceLine, self).default_get(fields_list)
        if self._context.get('default_enquiry_id', False):
            enquiry_id = self.env['airport.enquiry'].sudo().browse(self._context.get('default_enquiry_id'))
            airport_id = False
            if enquiry_id.service_type_id and enquiry_id.uaa_services_id:
                if enquiry_id.uaa_services_id == self.env.ref("sr_uaa_main.airport_transfer_services"):
                    if enquiry_id.service_type_id == self.env.ref("sr_uaa_main.arrival_service_type"):
                        airport_id = enquiry_id.pick_up_airport_id and enquiry_id.pick_up_airport_id.id or False
                    elif enquiry_id.service_type_id == self.env.ref("sr_uaa_main.departure_service_type"):
                        airport_id = enquiry_id.drop_off_airport_id and enquiry_id.drop_off_airport_id.id or False
                else:
                    airport_id = enquiry_id.airport_id and enquiry_id.airport_id.id or False
            res['airport_id'] = airport_id
        return res

