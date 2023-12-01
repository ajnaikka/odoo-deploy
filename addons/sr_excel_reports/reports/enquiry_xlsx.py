# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 SEEROO IT SOLUTIONS PVT.LTD(<https://www.seeroo.com/>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models
import string
from datetime import datetime, timedelta

from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import calendar
import base64
import io
import re
from odoo import api, models, _
import datetime
import calendar


class EnquiryXLSX(models.AbstractModel):
    _name = 'report.sr_excel_reports.enquiry_report_sr_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, record):

        # heading = workbook.add_format({'align': 'center',
        #                                'valign': 'vcenter',
        #                                'bold': True, 'size': 16})

        top_heading_left = workbook.add_format({'align': 'left',
                                                'valign': 'vcenter',
                                                'bold': True, 'size': 12})

        # top_heading_left1 = workbook.add_format({'align': 'right',
        #                                          'valign': 'vcenter',
        #                                          'bold': True, 'size': 12})

        format0 = workbook.add_format({'align': 'left',
                                       'valign': 'vcenter',

                                       'bold': False, 'size': 12})

        format1 = workbook.add_format({'num_format': '#,##0.00',
                                       'valign': 'vcenter', 'bold': False,
                                       'align': 'left', 'size': 12})

        # format2 = workbook.add_format({'num_format': '#,##0.00',
        #                                'valign': 'vcenter', 'bold': False,
        #                                'align': 'right', 'size': 12})
        # 
        # format3 = workbook.add_format({'align': 'left',
        #                                'valign': 'vcenter',
        #                                'bold': False, 'size': 12,
        #                                'color': 'red'})
        # format4 = workbook.add_format({'num_format': '#,##0.00',
        #                                'valign': 'vcenter', 'bold': False,
        #                                'align': 'right', 'size': 12,
        #                                'color': 'red'})

        start_date = datetime.datetime.strptime(data['start_date'], '%Y-%m-%d').strftime('%d-%b-%Y')
        end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d').strftime('%d-%b-%Y')

        dom = []

        if start_date:
            dom.append(('service_date', '>=', data['start_date']))
        if end_date:
            dom.append(('service_date', '<=', data['end_date']))

        if data.get('service_type_id', False):
            dom.append(('service_type_id', '=', data['service_type_id']))
        if data.get('status', False):
            dom.append(('status', '=', data['status']))
        if data.get('response_status_id', False):
            dom.append(('response_status_id', '=', data['response_status_id']))
        if data.get('payment_status', False):
            dom.append(('payment_status', '=', data['payment_status']))
        if data.get('email', False):
            dom.append(('email', '=', data['email']))
        if data.get('book_number', False):
            dom.append(('name', '=', data['book_number']))

        if data.get('uaa_services_id', False):
            dom.append(('uaa_services_id', '=', data['uaa_services_id']))

        enquiry_ids = self.env['airport.enquiry'].sudo().search(dom, order='service_date asc')
        worksheet = workbook.add_worksheet("service_name")
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 20)
        worksheet.set_column('D:D', 20)
        worksheet.set_column('E:E', 45)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 45)
        worksheet.set_column('H:H', 15)
        worksheet.set_column('I:I', 20)
        worksheet.set_column('J:J', 20)
        worksheet.set_column('K:K', 20)
        worksheet.set_column('L:L', 20)
        row = 0

        worksheet.write(row, 0, 'Date from' + ':', top_heading_left)
        worksheet.write(row, 1, start_date, format0)

        worksheet.write(row, 3, 'Date to' + ':', top_heading_left)
        worksheet.write(row, 4, end_date, format0)

        row += 1

        worksheet.write(row, 0, 'Serial No', top_heading_left)
        worksheet.write(row, 1, 'Booking Number', top_heading_left)
        worksheet.write(row, 2, 'Traveller', top_heading_left)
        worksheet.write(row, 3, 'Date of Request', top_heading_left)
        worksheet.write(row, 4, 'Airport Name', top_heading_left)
        worksheet.write(row, 5, 'Service Type', top_heading_left)
        worksheet.write(row, 6, 'Date of Service', top_heading_left)
        worksheet.write(row, 7, 'Response Status', top_heading_left)
        worksheet.write(row, 8, 'Payment Status', top_heading_left)
        # worksheet.write(row, 9, 'Date of Payment', top_heading_left)
        worksheet.write(row, 9, 'Enquiry Status', top_heading_left)
        worksheet.write(row, 10, 'Contact Number', top_heading_left)
        row += 1
        count = 1
        if enquiry_ids:
            for line in enquiry_ids:
                worksheet.write(row, 0, count, format0)
                count += 1
                worksheet.write(row, 1, line.name or ' ', format1)
                worksheet.write(row, 2, line.traveler_name or ' ', format1)
                worksheet.write(row, 3, line.request_date and str(line.request_date) or ' ', format1)
                if line.airport_id:
                    worksheet.write(row, 4, line.airport_id.name or '', format1)
                if line.service_type_id:
                    worksheet.write(row, 5, line.service_type_id.name, format1)
                worksheet.write(row, 6, line.services_on or ' ', format1)
                if line.response_status_id:
                    worksheet.write(row, 7, line.response_status_id.name or '', format1)
                if line.payment_status:
                    worksheet.write(row, 8, dict(self.env['enquiry.wizard']._fields['payment_status'].selection).get(
                        line.payment_status) or '', format1)
                # worksheet.write(row, 9, line.payment_date and str(line.payment_date) or '', format1)
                if line.status:
                    worksheet.write(row, 9,
                                    dict(self.env['enquiry.wizard']._fields['status'].selection).get(line.status) or '',
                                    format1)
                worksheet.write(row, 10, line.contact_number or '', format1)
                row += 1
