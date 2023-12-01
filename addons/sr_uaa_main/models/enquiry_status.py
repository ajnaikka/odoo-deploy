from odoo import models, fields, api, _


class EnquiryStatus(models.Model):
    _name = 'enquiry.status'
    _description = 'Enquiry Status Comment'

    name = fields.Text('Comment', required=True)
    airport_enquiry_id = fields.Many2one('airport.enquiry')
    enquiry_id = fields.Many2one('airport.enquiry', string="Enquiry", copy=False)

    def get_enquiry(self):
        self.ensure_one()
        if self.enquiry_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Enquiry',
                'view_mode': 'form',
                'res_model': 'airport.enquiry',
                'res_id': self.enquiry_id.id,
                # 'domain': [('enquiry_id', '=', self.id)],
                'context': "{'create': False,'edit': False,'delete': False}",
                'target': 'new',
            }
