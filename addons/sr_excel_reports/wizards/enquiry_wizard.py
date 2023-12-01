# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date
import time
import calendar
import datetime


class EnquiryWizard(models.TransientModel):
    _name = 'enquiry.wizard'

    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date', default=date.today())
    book_number = fields.Char('Booking Number')
    email = fields.Char('Email')
    payment_status = fields.Selection([('pending', 'Pending'),
                                       ('cancel', 'Cancelled'),
                                       ('done', 'Completed')], string="Payment Status")
    response_status_id = fields.Many2one('response.status.name','Response Status')
    status = fields.Selection([('new', 'New'),
                                ('open', 'Open'),
                               ('close', 'Closed'),
                               ('cancel', 'Cancelled')],
                              string='Enquiry Status')
    airport_id = fields.Many2one('admin.airport', 'Airport Name', required=True)
    service_type_id = fields.Many2one('airport.service.type',
                                    string='Service Type')
    uaa_services_id = fields.Many2one('uaa.services', string='Services')

    # @api.model
    # def default_get(self, fields):
    #     res = super(EnquiryWizard, self).default_get(fields)
    #     today_date = date.today()
    #     start_date = datetime.date(today_date.year, today_date.month, 1)
    #     res['start_date'] = start_date
    #     return res

    def print_xlsx_report(self):
        data = {'start_date': self.start_date,
                'end_date': self.end_date,
                'uaa_services_id': self.uaa_services_id and self.uaa_services_id.id or False,
                'service_type_id': self.service_type_id and self.service_type_id.id or False,
                'status': self.status,
                'response_status_id': self.response_status_id and self.response_status_id.id or False,
                'payment_status': self.payment_status,
                'email': self.email,
                'book_number': self.book_number,
                'airport_id': self.airport_id,

                }
        return self.env.ref('sr_excel_reports.sr_enquiry_report_xlsx').report_action(self, data=data)


