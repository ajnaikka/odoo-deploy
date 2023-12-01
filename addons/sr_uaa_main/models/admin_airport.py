from odoo import models, fields, api


class AdminAirport(models.Model):
    _name = 'admin.airport'
    _description = 'Airport Details'
    _order = 'name asc'

    @api.depends('enquiry_ids')
    def compute_enquiry_count(self):
        for record in self:
            enquiry_count = 0
            if record.enquiry_ids:
                enquiry_count = len(record.enquiry_ids)
            record.enquiry_count = enquiry_count
            print(enquiry_count,"@@@@@@@@@@@@@@")

    country_id = fields.Many2one('res.country', string='Country')
    name = fields.Char('Airport')
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Airport Code')
    enquiry_count = fields.Integer('Enquiry Count',
                                   compute="compute_enquiry_count", store=True)
    enquiry_ids = fields.One2many('airport.enquiry', 'airport_id', 'Enquires')
    service_ids = fields.One2many('service.line', 'airport_id', string='Enquiry Services')
    service_line_ids = fields.One2many('airport.service.line', 'airport_id', string='Airport Services')

    def get_enquiry(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enquiry',
            'view_mode': 'tree,form',
            'res_model': 'airport.enquiry',
            'domain': [('airport_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name += ' (' + record.code + ') '
            if record.country_id and record.country_id.name:
                name += ' / ' + record.country_id.name
            res.append((record.id, name))
        return res
