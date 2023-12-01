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
from odoo import api, fields, models, _, tools
import datetime
import tempfile
import base64
import os
from odoo.exceptions import Warning as UserError
import logging

_logger = logging.getLogger(__name__)

try:
    import xlrd

    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

from datetime import datetime, timedelta


class EnquiryImport(models.TransientModel):
    _name = 'enquiry.import'
    _description = 'Import Enquiries'

    file = fields.Binary('File', help="FIle to import, only CSV files", attachment=False, filename="filename")
    filename = fields.Char(string="Filename")

    def process_file(self):
        if not self.file:
            raise Warning(_('File not selected !'))
        tmp = tempfile.NamedTemporaryFile(suffix='.xls').name
        with open(os.path.expanduser(tmp), 'wb') as fout:
            fout.write(base64.b64decode(self.file))
        workbook = xlrd.open_workbook(tmp)
        worksheet = workbook.sheet_by_index(0)
        first_row = []
        for col in range(worksheet.ncols):
            first_row.append(worksheet.cell_value(0, col))
        data = []
        for row in range(1, worksheet.nrows):
            elm = {}
            for col in range(worksheet.ncols):
                elm[first_row[col]] = worksheet.cell_value(row, col)
            data.append(elm)
        return data

    def airport_import(self):
        data = self.process_file()
        if data:
            AirportTemplate = self.env['admin.airport'].sudo()
            uaa_services = self.env['uaa.services'].sudo()
            uaa_services_type = self.env['airport.service.type'].sudo()
            uaa_service_category = self.env['airport.service.line'].sudo()
            service_category_pool = self.env['service.category'].sudo()
            service_line_pool = self.env['service.line'].sudo()
            updated_list = []
            count = 0
            count_total = len(data)
            for line in data:
                count += 1
                _logger.info('Import %s -> %s', count, count_total)
                airport_val = {}
                service_val = {}
                service_list = []
                category_vals = {}
                categ_list = []
                domain = []
                country_id = False

                if line.get('Airport Name', ''):
                    name = line.get('Airport Name', '')
                    domain += [('name', '=', name)]
                    if line.get('Airport Code', ''):
                        code = line.get('Airport Code', '')
                        domain += [('code', '=', code)]

                    if line.get('Country', ''):
                        country = line.get('Country', '')
                        country_id = self.env['res.country'].sudo().search([('name', '=', country_id)], limit=1)

                    airport_obj = AirportTemplate.search(domain, limit=1)
                    # if not airport_obj:
                    #     raise UserError("Invalid Airport Name %s" %name)

                    if airport_obj:
                        service_val.update({
                            'airport_id': airport_obj.id,
                        })
                        if line.get('Services', ''):
                            service = line.get('Services', '')
                            check_service_id = uaa_services.search([('name', '=', service.upper())], limit=1)
                            if check_service_id:
                                service_val.update({
                                    'uaa_services_id': check_service_id.id,
                                })
                                category_vals.update({
                                    'uaa_services_id': check_service_id.id,
                                })
                        if line.get('Service Category', ''):
                            category_vals.update({'airport_id': airport_obj.id, })
                            service_cat_type = line.get('Service Category', '')
                            n = len(service_cat_type.split('\n'))
                            for i in range(n):
                                val = service_cat_type.split('\n')[i].split('=')
                                categ_list.append(val)
                                i = i + 1
                                n = n - 1

                        if line.get('Service type', ''):
                            service_type = line.get('Service type', '')
                            check_service_type_id = uaa_services_type.search([('name', '=', service_type)], limit=1)
                            if check_service_type_id:
                                service_val.update({
                                    'service_type_id': check_service_type_id.id,
                                })
                                category_vals.update({
                                    'service_type_id': check_service_type_id.id,
                                })

                                service_line_id = service_line_pool.create(service_val)
                            if categ_list:
                                for categ in categ_list:
                                    service_category_id = service_category_pool.search(
                                        [('name', '=', str(categ[0].strip()))], limit=1)
                                    if service_category_id:
                                        if not self.isfloat(categ[1]):
                                            raise UserError("Invalid amount : %s in %s" % (categ[1], name))
                                        category_vals.update({
                                            'service_category_id': service_category_id.id,
                                            'amount': float(categ[1].strip()),
                                            'service_id': service_line_id.id,
                                        })
                                        uaa_service_category.create(category_vals)

                    else:
                        if country_id:
                            check_airport_id = AirportTemplate.search([
                                ('name', '=', line.get('Airport Name', '')),
                                ('code', '=', line.get('Airport Code', '')),
                                ('country_id', '=', country_id.id)
                            ], limit=1)
                            if not check_airport_id:
                                airport_val.update({
                                    'name': line.get('Airport Name', ''),
                                    'code': line.get('Airport Code', ''),
                                    'country_id': country_id and country_id.id or False,
                                })
                                if line.get('Services', ''):
                                    service = line.get('Services', '')
                                    check_service_id = uaa_services.search([('name', '=', service.upper())], limit=1)
                                    if check_service_id:
                                        service_val.update({
                                            'uaa_services_id': check_service_id.id,
                                        })
                                        category_vals.update({
                                            'uaa_services_id': check_service_id.id,
                                        })

                                if line.get('Service type', ''):
                                    service_type = line.get('Service type', '')
                                    check_service_type_id = uaa_services_type.search([('name', '=', service_type)],
                                                                                     limit=1)
                                    if check_service_type_id:
                                        service_val.update({
                                            'service_type_id': check_service_type_id.id,
                                        })
                                        category_vals.update({
                                            'service_type_id': check_service_type_id.id,
                                        })
                                if airport_val:
                                    airport_id = AirportTemplate.create(airport_val)

                                    categ_list = []
                                    if line.get('Service Category', ''):
                                        service_cat_type = line.get('Service Category', '')
                                        n = len(service_cat_type.split('\n'))
                                        for i in range(n):
                                            val = service_cat_type.split('\n')[i].split('=')
                                            categ_list.append(val)
                                            i = i + 1
                                            n = n - 1
                                    service_val.update({'airport_id': airport_id.id, })
                                    if service_val.get('uaa_services_id'):
                                        service_line_id = service_line_pool.create(service_val)
                                    if categ_list:
                                        for categ in categ_list:
                                            service_category_id = service_category_pool.search(
                                                [('name', '=', str(categ[0].strip()))], limit=1)
                                            if service_category_id:
                                                category_vals.update({
                                                    'service_category_id': service_category_id.id,
                                                    'amount': float(categ[1].strip()),
                                                    'service_id': service_line_id.id,
                                                    'airport_id': airport_id.id,
                                                })
                                                uaa_service_category.create(category_vals)
                                    updated_list.append(airport_id.id)

            _logger.info('Updated: %s', updated_list)

    def isfloat(self, num):
        try:
            float(num)
            return True
        except ValueError:
            return False

    def enquiry_import(self, *args, **kwargs):
        data = self.process_file()
        if data:
            print("datA", data)
            AirportTemplate = self.env['admin.airport'].sudo()
            EnquiryTemplate = self.env['airport.enquiry'].sudo()
            updated_list = []
            count = 0
            count_total = len(data)

            for line in data:
                print("line", line)
                count += 1
                _logger.info('Import %s -> %s', count, count_total)

                airport_id = False

                enquiry_val = {}

                if line.get('Airport Name', ''):
                    txt = line.get('Airport Name', '')
                    x = txt.split('(')[0].rstrip()
                    airport_id = AirportTemplate.search([('name', '=', x)], limit=1)

                    if not airport_id:
                        airport_val = {}
                        txt = line.get('Airport Name', '')
                        x = txt.split('(')[0].rstrip()
                        y = txt.split('(')[1].split(')')[0].rstrip()
                        z = txt.split('/')[-1].strip()
                        country_id = self.env['res.country'].sudo().search([('country_id', '=', z)], limit=1)

                        if country_id:
                            check_airport_id = AirportTemplate.search([
                                ('name', '=', x),
                                ('code', '=', y),
                                ('country_id', '=', country_id.id)
                            ], limit=1)

                            if not check_airport_id:
                                airport_val.update({
                                    'name': x,
                                    'code': y,
                                    'country_id': country_id and country_id.id or False,
                                })

                                if airport_val:
                                    airport_id = AirportTemplate.create(airport_val)
                request_date = False
                service_date = False
                arrival_date = False
                departure_date = False

                if line.get('Service Date'):
                    service1_date = line.get('Service Date')
                    epoch = datetime(1899, 12, 30)
                    delta_days = timedelta(days=service1_date)
                    service_date = epoch + delta_days
                    # try:
                    #     service_date = datetime.datetime.strptime(service_date, '%d - %b - %Y').strftime(
                    #         '%Y-%m-%d')
                    #     if line.get('Service Date', False):
                    #         if line.get('Service Date', False) != '':
                    #             service_date += ' ' + line.get('Service Date')
                    #             service_date = datetime.datetime.strptime(service_date,
                    #                                                       '%d - %b - %Y %H:%M').strftime(
                    #                 '%Y-%m-%d %H:%M:%S')
                    #         else:
                    #             service_date = datetime.datetime.strptime(service_date, '%d - %b - %Y').strftime(
                    #                 '%Y-%m-%d 00:00:00')
                    #     else:
                    #         service_date = datetime.datetime.strptime(service_date, '%d - %b - %Y').strftime(
                    #             '%Y-%m-%d 00:00:00')
                    # except Exception as e:
                    #     print("exce", str(e))
                    #     # request_date = False
                    #     service_date = False

                if line.get('Arrival Date', False):
                    arrival_date = line.get('Arrival Date', False)
                    try:
                        if line.get('Arrival Time', False):
                            if line.get('Arrival Time', False) != '':
                                arrival_date += ' ' + line.get('Arrival Time')

                                arrival_date = datetime.datetime.strptime(arrival_date, '%d - %b - %Y %H:%M').strftime(
                                    '%Y-%m-%d %H:%M:%S')
                            else:
                                arrival_date = datetime.datetime.strptime(arrival_date, '%d - %b - %Y').strftime(
                                    '%Y-%m-%d 00:00:00')
                        else:
                            arrival_date = datetime.datetime.strptime(arrival_date, '%d - %b - %Y').strftime(
                                '%Y-%m-%d 00:00:00')
                    except:
                        arrival_date = False

                if line.get(' Departure Date', False):
                    departure_date = line.get('Departure Date', False)
                    try:
                        if line.get('Departure Time', False):
                            if line.get('Departure Time', False) != '':
                                departure_date += ' ' + line.get('Departure Time')
                                departure_date = datetime.datetime.strptime(departure_date,
                                                                            '%d - %b - %Y %H:%M').strftime(
                                    '%Y-%m-%d %H:%M:%S')
                            else:
                                departure_date = datetime.datetime.strptime(departure_date, '%d - %b - %Y').strftime(
                                    '%Y-%m-%d 00:00:00')
                        else:
                            departure_date = datetime.datetime.strptime(departure_date, '%d - %b - %Y').strftime(
                                '%Y-%m-%d 00:00:00')
                    except:
                        departure_date = False

                mobile = ''
                code = ''
                country_id = False
                if line.get('Mobile', False):
                    if len(str(line.get('Mobile')).split(' ')) > 1:
                        mobile = str(line.get('Mobile')).split(' ')[1]
                        if len(str(line.get('Mobile')).split(' ')[0].split('+')) > 1:
                            code = str(line.get('Mobile')).split(' ')[0].split('+')[1]
                            country_id = self.env['res.country'].search([('phone_code', '=', code)], limit=1)
                    else:
                        code = ''
                        mobile = str(line.get('Mobile')).split(' ')[0]
                flight_number = ''
                if line.get('Flight number'):
                    if line.get('Flight number') != '':
                        flight_number = line.get('Flight number')
                service_type = ''
                if line.get('Service Type', False):
                    if line.get('Service Type') == 'Arrival Service' or 1:
                        service_type = 'arrival'
                        enquiry_val.update({
                            'arrival_flight_number': flight_number,
                        })
                    elif line.get('Service Type') == 'Departure Service' or 2:
                        service_type = 'departure'
                        enquiry_val.update({
                            'departure_flight_number': flight_number,
                        })
                    elif line.get('Service Type') == 'Transit Service' or 3:
                        service_type = 'transit'
                service_ids = []
                if line.get('Services', False):
                    services_a = line.get('Services')
                    services = str(services_a).split(', ')
                    for ser in services:
                        if ser == 'Meet and Greet' or 1:
                            service_ids.append(self.env.ref('sr_uaa_main.meet_greet_airport_service_name').id)
                        if ser == 'VIP Fast Track Clearance' or 3:
                            service_ids.append(
                                self.env.ref('sr_uaa_main.vip_fast_track_clearance_airport_service_name').id)
                        if ser == 'Premium taxi / Limousine' or 5:
                            service_ids.append(self.env.ref('sr_uaa_main.premium_taxi_airport_service_name').id)
                        if ser == 'Airport Lounge' or 4:
                            service_ids.append(self.env.ref('sr_uaa_main.airport_lounge_airport_service_name').id)
                        if ser == 'Check-in Assistance' or 2:
                            service_ids.append(self.env.ref('sr_uaa_main.checkin_assistance_airport_service_name').id)

                adults = 0
                children = 0
                if line.get('Adults', False):
                    if line.get('Adults', False) != '':
                        adults = int(line.get('Adults', 0))

                if line.get('Children', False):
                    if line.get('Children') != '':
                        children = int(line.get('Children', 0))

                infants = 0
                is_infant = False
                if line.get('Infants', False):
                    if line.get('Infants', False) != '':
                        infants = int(line.get('Infants', 0))
                        if infants > 0:
                            is_infant = True

                cust_message = ''
                if line.get('Customer Message'):
                    if line.get('Customer Message') != '':
                        cust_message = line.get('Customer Message')

                status = ''
                if line.get('Status'):
                    if line.get('Status') == 'Open':
                        status = 'open'
                    elif line.get('Status') == 'Closed':
                        status = 'close'
                payment_status = ''
                if line.get('Payment Status'):
                    if line.get('Payment Status') != '':
                        if line.get('Payment Status') == 'Hold Verification':
                            payment_status = 'in_payment'
                        if line.get('Payment Status') == 'Pending':
                            payment_status = 'not_paid'
                        if line.get('Payment Status') == 'Declined':
                            payment_status = 'not_paid'
                        if line.get('Payment Status') == 'Cancelled':
                            payment_status = 'not_paid'
                        if line.get('Payment Status') == 'Not Paid':
                            payment_status = 'not_paid'
                        if line.get('Payment Status') == 'Complete':
                            payment_status = 'paid'
                        if line.get('Payment Status') == 'In Payment':
                            payment_status = 'in_payment'
                        if line.get('Payment Status') == 'Paid':
                            payment_status = 'paid'
                        if line.get('Payment Status') == 'Partially Paid':
                            payment_status = 'partial'
                        if line.get('Payment Status') == 'Reversed':
                            payment_status = 'reversed'
                        if line.get('Payment Status') == 'Invoicing App Legacy':
                            payment_status = 'invoicing_legacy'

                response_status_id = False
                if line.get('Response Status'):
                    if line.get('Response Status') != '':
                        if line.get('Response Status') == 'New Enquiry':
                            response_status_id = self.env.ref('sr_uaa_main.new_enquiry_response_status').id
                        if line.get('Response Status') == 'Quotation Sent':
                            response_status_id = self.env.ref('sr_uaa_main.payment_link_sent_response_status').id

                        if line.get('Response Status') == 'Additional Quotation Sent':
                            response_status_id = self.env.ref(
                                'sr_uaa_main.additional_payment_link_sent_response_status').id

                        if line.get('Response Status') == 'Payment Completed':
                            response_status_id = self.env.ref('sr_uaa_main.payment_completed_response_status').id
                        if line.get('Response Status') == 'Service Confirmed':
                            response_status_id = self.env.ref('sr_uaa_main.service_confirmed_response_status').id
                        if line.get('Response Status') == 'Payment Received':
                            response_status_id = self.env.ref('sr_uaa_main.payment_received_response_status').id
                        if line.get('Response Status') == 'Service Requested':
                            response_status_id = self.env.ref('sr_uaa_main.service_request_sent_response_status').id
                        if line.get('Response Status') == 'Confirmation Voucher Sent':
                            response_status_id = self.env.ref(
                                'sr_uaa_main.confirmation_voucher_sent_response_status').id
                        if line.get('Response Status') == 'Cancelled':
                            response_status_id = self.env.ref('sr_uaa_main.cancelled_response_status').id
                        if line.get('Response Status') == 'Service Completed':
                            response_status_id = self.env.ref('sr_uaa_main.service_completed_response_status').id
                        if line.get('Response Status') == 'Service Not Rendered And Refunded':
                            response_status_id = self.env.ref(
                                'sr_uaa_main.service_not_rendered_refunded_response_status').id
                        if line.get('Response Status') == 'Service Not Rendered And Not Refunded':
                            response_status_id = self.env.ref(
                                'sr_uaa_main.service_not_rendered_not_refunded_response_status').id

                driver_contact = ''
                if line.get('Driver Contact No', False):
                    if line.get('Driver Contact No') != '':
                        driver_contact = line.get('Driver Contact No')

                Email = ''
                if line.get('Email'):
                    if line.get('Email') != '':
                        Email = line.get('Email')
                traveler_name = ''
                if line.get('Name of the Traveller'):
                    if line.get('Name of the Traveller') != '':
                        traveler_name = line.get('Name of the Traveller')

                travel_class_id = False
                if line.get('Class of Travel'):
                    if line.get('Class of Travel') != '':
                        if line.get('Class of Travel') == 'First Class':
                            travel_class_id = self.env.ref('sr_uaa_main.first_class_travel').id
                        if line.get('Class of Travel') == 'Economy':
                            travel_class_id = self.env.ref('sr_uaa_main.economy_class_travel').id
                        if line.get('Class of Travel') == 'Premium Economy':
                            travel_class_id = self.env.ref('sr_uaa_main.premium_economy_class_travel').id
                        if line.get('Class of Travel') == 'Business Class':
                            travel_class_id = self.env.ref('sr_uaa_main.business_class_travel').id

                uaa_services_id = False
                if line.get('Service'):
                    if line.get('Service') != '':
                        if line.get('Service') == 'MEET & GREET':
                            uaa_services_id = self.env.ref('sr_uaa_main.meet_greet_services').id
                        if line.get('Service') == 'AIRPORT HOTEL':
                            uaa_services_id = self.env.ref('sr_uaa_main.airport_hotel_services').id
                        if line.get('Service') == 'AIRPORT TRANSFER':
                            uaa_services_id = self.env.ref('sr_uaa_main.airport_transfer_services').id
                        if line.get('Service') == 'AIRPORT LOUNGE':
                            uaa_services_id = self.env.ref('sr_uaa_main.airport_lounge_services').id

                estimated_service_fee = False
                if line.get('Service Fee'):
                    if line.get('Service Fee') != '':
                        estimated_service_fee = line.get('Service Fee')

                enquiry_val.update({
                    'airport_id': airport_id and airport_id.id or False,
                    'traveler_name': traveler_name,
                    'email': Email,
                    'payment_status': payment_status,
                    'request_date': request_date,
                    'service_date': service_date,
                    'arrival_date_str': str(arrival_date),
                    'departure_date_str': str(departure_date),
                    'country_id': country_id and country_id.id or False,
                    'country_code': code or '',
                    'contact_number': mobile,
                    'service_type': service_type,
                    'services_ids': [(6, 0, service_ids)],
                    'adults_count': adults,
                    'children_count': children,
                    'infants_count': infants,
                    'need_wheelchair': is_infant,
                    'wheelchair_count': infants,
                    'travelers_count': adults + children,
                    'customer_message': cust_message,
                    'travel_class_id': travel_class_id,
                    'uaa_services_id': uaa_services_id,
                    'estimated_service_fee': estimated_service_fee,
                    'drivers_contact_number': driver_contact,
                })
                if enquiry_val:
                    print("enqq", enquiry_val)
                    enquiry_id = EnquiryTemplate.create(enquiry_val)
                    updated_list.append(enquiry_id.id)

                _logger.info('Updated: %s', updated_list)

    def airport_service_description(self):
        data = self.process_file()
        if data:
            airport_template = self.env['admin.airport'].sudo()
            uaa_services = self.env['uaa.services'].sudo()
            airport_services_type = self.env['airport.service.type'].sudo()
            airport_service_category = self.env['airport.service.line'].sudo()
            service_category_pool = self.env['service.category'].sudo()
            service_line_pool = self.env['service.line'].sudo()
            dom = []

            for line in data:
                domain = []
                country_id = False
                # if line.get('Origin Code', ''):
                #     txt = line.get('Origin Code', '')
                #     # x = txt.split('(')[0].strip()
                #     # y = txt.split('(')[1].split(')')[0].strip()
                #     # z = txt.split('/')[-1].strip()
                #     try:
                #         x = txt.split('(')[0].strip()
                #     except:
                #         x = ''
                #     try:
                #         y = txt.split('(')[1].split(')')[0].strip()
                #     except:
                #         y = ''
                #     try:
                #         z = txt.split('/')[-1].strip()
                #     except:
                #         z = ''
                if line.get('Airport Name', ''):
                    name = line.get('Airport Name', '')
                    # domain += [('name', '=', name)]
                    if line.get('Airport Code', ''):
                        code = line.get('Airport Code', '')
                        domain += [('code', '=', code)]

                    if line.get('Country', ''):
                        country = line.get('Country', '')
                        country_id = self.env['res.country'].sudo().search([('name', '=', country)], limit=1)

                    airport_obj = airport_template.search(domain, limit=1)
                    service_val = {}
                    category_vals = {}
                    if airport_obj:
                        dom.append(('airport_id', '=', airport_obj.id))

                        if line.get('Services', ''):
                            service = line.get('Services', '')
                            check_service_id = uaa_services.search([('name', '=', service.upper())], limit=1)
                            if check_service_id:
                                service_val.update({
                                    'uaa_services_id': check_service_id.id,
                                })
                                dom.append(('uaa_services_id', '=', check_service_id.id))

                        if line.get('Service Type', ''):
                            service_type = line.get('Service Type', '')
                            check_service_type_id = airport_services_type.search([('name', '=', service_type)], limit=1)
                            if check_service_type_id:
                                service_val.update({
                                    'service_type_id': check_service_type_id.id,
                                })
                                dom.append(('service_type_id', '=', check_service_type_id.id))

                        if line.get('Service Category', ''):
                            service_cat_type = line.get('Service Category', '')
                            check_service_cat_type = service_category_pool.search([('name', '=', service_cat_type)],
                                                                                  limit=1)
                            if check_service_cat_type:
                                service_val.update({
                                    'service_category_id': check_service_cat_type.id,
                                })
                                dom.append(('service_category_id', '=', check_service_cat_type.id))

                        if line.get('Description', ''):
                            description = line.get('Description', '')
                            description_line = description.split('\n')

                            html = "<p>"
                            for each_line in description_line:
                                html += "%s" % each_line + "<br/>"
                            html += "</p>"
                            # html = "<p>%s</p>" % description

                            service_val.update({
                                'description': html,
                            })
                            service_avial = airport_service_category.search(dom, limit=1)
                            dom = []
                            if service_avial:
                                service_avial.write(service_val)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
