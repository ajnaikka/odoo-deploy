from odoo import http,SUPERUSER_ID
from odoo.http import request

import re
import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
Integerregex = r'^\d+$'
DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%d %H:%M'
DEFAULT_FACTURE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


class AirportHotel(http.Controller):

    def checkString(self, str):
        flag_l = False
        flag_n = False
        for i in str:
            if i.isalpha():
                flag_l = True
            if i.isdigit():
                flag_n = True
        return (flag_l and flag_n)

    def validate_phone(self, phone):
        # regex_phone = r'^(\+0?1\s)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}'
        regex_phone = r'^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{1,4})(?: *x(\d+))?\s*'
        if re.fullmatch(regex_phone, phone):
            return True
        else:
            return False

    def convert_local_time_to_utc(self, date_str=False,
                                  timeZone=""):
        if (not timeZone):
            timeZone = request.env.context.get("tz") or request.env.user.tz or "UTC"
        display_date_result = False
        if date_str:
            user_tz = pytz.timezone(timeZone)
            dateformat_obj = datetime.strptime(str(date_str), DEFAULT_FACTURE_DATE_FORMAT)
            date_start = user_tz.localize(dateformat_obj).astimezone(pytz.timezone("UTC"))
            display_date_result = date_start.strftime(DEFAULT_FACTURE_DATE_FORMAT)
        return display_date_result

    @http.route('/airport-hotel-form', type='http', auth='public', website=True, methods=['GET','POST'], csrf=False)
    def request_airport_hotel_details(self, **post):
        error = {}
        values = {}
        success = False
        booking_ref = False
        
        uaa_services = request.env['uaa.services'].sudo().search([])
        airport_enquiry = request.env['airport.enquiry'].sudo().search([])
        airports = request.env['admin.airport'].sudo().search([])
        airport_service = request.env['airport.service.name'].sudo().search([])
        country = request.env['res.country'].sudo().search([])
        service_type_ids = request.env['airport.service.type'].sudo().search([])
        # service_type_ids = request.env.ref("sr_uaa_main.airport_hotel_services").sudo().service_type_ids
        travel_class_ids = request.env['travel.class'].sudo().search([])

        title = request.env.ref("sr_uaa_main.airport_hotel_services").sudo().name
        hours = []
        minutes = []
        for hour in range(24):
            hours.append(f"{hour:02d}")
        for minute in range(60):
            minutes.append(f"{minute:02d}")
        values.update({
            'hours': hours,
            'minutes': minutes,
        })

        values.update({
            'title': title,
            'arrival_hours_id': '',
            'arrival_minutes_id': '',
            'departure_hours_id': '',
            'departure_minutes_id': '',
            'airport_enquiry': airport_enquiry,
            'airport_names': airports,
            'services': airport_service,
            'country': country,
            'airport_name': '',
            'traveler_name': '',
            'email': '',
            'contact_number': '',
            'country_id': '',
            'service_types': '',
            'service_types_name': 'arrival',
            # 'services_ids': [],
            'arrival_flight_number': '',
            'departure_flight_number': '',
            'hours_count': '',
            'adults_count': '',
            'customer_message': '',
            'enqcaptcha': '',
                })
        if post and request.httprequest.method == 'POST':
            if not post.get('airport_id', False):
                error.update({
                    'airport_id': 'Airport Name is missing!'
                })
            if not post.get('traveler_name', False):
                error.update({
                    'traveler_name': 'Traveller Name is missing!'
                })
            elif any(character.isdigit() for character in post.get('traveler_name')):
                error.update({
                    'traveler_name': 'Traveller Name Contains Numbers!'
                })
            if not post.get('email', False):
                error.update({
                    'email': 'Email Address is missing!!'
                })
            elif not re.fullmatch(regex, post.get('email', False)):
                error.update({
                    'email': 'Please enter a valid email address!'
                })
            if not post.get('contact_number', False):
                error.update({
                    'country_id': 'Contact Number is missing!',
                    'contact_number': 'MISSING'
                })
            # elif not self.validate_phone(post.get('contact_number')):
            #     error.update({
            #         'country_id': 'Contact Number is invalid!',
            #         'contact_number': 'MISSING'
            #     })

            if not post.get('country_id', False):
                error.update({
                    'country_id': 'Country code is missing!'

                })
                if not post.get('contact_number', False):
                    error.update({
                        'country_id': 'Country Code and Contact Number is missing!',
                        'contact_number': 'MISSING'
                    })
                # elif not self.validate_phone(post.get('contact_number')):
                #     error.update({
                #         'country_id': 'Country Code is missing and Contact Number is invalid!',
                #         'contact_number': 'MISSING'
                #     })
            if not post.get('service_types', False):
                error.update({
                    'service_types': 'Service Type is missing!'
                })
                service_type_id = False
            else:
                service_type_id = request.env['airport.service.type'].sudo().browse(int(post.get('service_types')))
            if service_type_id:
                if service_type_id.is_arrival:
                    if not post.get('arrival_flight_number', False):
                        error.update({
                            'arrival_flight_number': 'Arrival Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('arrival_flight_number')):
                    #     error.update({
                    #         'arrival_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('arrival_date', False):
                        error.update({
                            'arrival_date': 'Arrival Date is missing!'
                        })
                    if not post.get('arrival_hours_id', False):
                        error.update({
                            'arrival_time': 'Hour is missing!'
                        })
                        if not post.get('arrival_minutes_id', False):
                            error.update({
                                'arrival_time': 'Arrival Time is missing!'
                            })
                    elif not post.get('arrival_minutes_id', False):
                        error.update({
                            'arrival_time': 'Minute is missing!'
                        })

                elif service_type_id.is_departure:
                    if not post.get('departure_flight_number', False):
                        error.update({
                            'departure_flight_number': 'Departure Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('departure_flight_number')):
                    #     error.update({
                    #         'departure_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('departure_date', False):
                        error.update({
                            'departure_date': 'Departure Date is missing!'
                        })
                    if not post.get('departure_hours_id', False):
                        error.update({
                            'departure_time': 'Hour is missing!'
                        })
                        if not post.get('departure_minutes_id', False):
                            error.update({
                                'departure_time': 'Departure Time is missing!'
                            })
                    elif not post.get('departure_minutes_id', False):
                        error.update({
                            'departure_time': 'Minute is missing!'
                        })

                elif service_type_id.is_transit:
                    if not post.get('arrival_flight_number', False):
                        error.update({
                            'arrival_flight_number': 'Arrival Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('arrival_flight_number')):
                    #     error.update({
                    #         'arrival_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('arrival_date', False):
                        error.update({
                            'arrival_date': 'Arrival Date is missing!'
                        })
                    if not post.get('arrival_hours_id', False):
                        error.update({
                            'arrival_time': 'Hour is missing!'
                        })
                        if not post.get('arrival_minutes_id', False):
                            error.update({
                                'arrival_time': 'Arrival Time is missing!'
                            })
                    elif not post.get('arrival_minutes_id', False):
                        error.update({
                            'arrival_time': 'Minute is missing!'
                        })
                    if not post.get('departure_flight_number', False):
                        error.update({
                            'departure_flight_number': 'Departure Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('departure_flight_number')):
                    #     error.update({
                    #         'departure_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('departure_date', False):
                        error.update({
                            'departure_date': 'Departure Date is missing!'
                        })
                    if not post.get('departure_hours_id', False):
                        error.update({
                            'departure_time': 'Hour is missing!'
                        })
                        if not post.get('departure_minutes_id', False):
                            error.update({
                                'departure_time': 'Departure Time is missing!'
                            })
                    elif not post.get('departure_minutes_id', False):
                            error.update({
                                'departure_time': 'Minute is missing!'
                            })

            if post.get('hours_count', False):
                if not re.fullmatch(Integerregex, post.get('hours_count', False)):
                    error.update({
                        'hours_count': 'Value should be a positive number!'
                    })
            if not post.get('hours_count', False):
                error.update({
                    'hours_count': 'No of hours of stay is missing!'
                })
            if post.get('travelers_count', False):
                if not re.fullmatch(Integerregex, post.get('travelers_count', False)):
                    error.update({
                        'travelers_count': 'Value should be a positive number!'
                    })
            if not post.get('travelers_count', False):
                error.update({
                    'travelers_count': 'No of Travellers is missing!'
                })
            # if not post.get('customer_message', False):
            #     error.update({
            #         'customer_message': 'Message is missing!'
            #     })

            services = []
            services_list = [key for key, v in post.items() if key.startswith('servicesinput_')]
            if services_list:
                for serv_list in services_list:
                    ser_id = int(serv_list.split('_')[1])
                    services.append(ser_id)
            arrival_date_time = False
            departure_date_time = False
            service_date = False
            if service_type_id:
                if service_type_id.is_arrival:
                    if post.get('arrival_date', False) and post.get('arrival_hours_id', False) and post.get('arrival_minutes_id', False):
                        arrival_date_time_str = post['arrival_date'] + ' ' + post['arrival_hours_id'] + ':' + post['arrival_minutes_id']
                        arrival_date_time = datetime.strptime(arrival_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                        formatted_time_arrival = arrival_date_time.strftime('%d/%m/%Y %H:%M')
                        if arrival_date_time <= datetime.today():
                            error.update({
                                'arrival_date': 'Date should be greater than Today!',
                                'arrival_time': 'Arrival Time is Incorrect!'
                            })
                        arrival_date_time = formatted_time_arrival + ':00'
                        service_date = datetime.strptime(post['arrival_date'], '%Y-%m-%d')
                        # arrival_date_time = arrival_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # arrival_date_time = self.convert_local_time_to_utc(arrival_date_time, post.get('timezone'))

                elif service_type_id.is_departure:
                    if post.get('departure_date', False) and post.get('departure_hours_id', False) and post.get('departure_minutes_id', False):
                        departure_date_time_str = post['departure_date'] + ' ' + post['departure_hours_id'] + ':' + post['departure_minutes_id']
                        departure_date_time = datetime.strptime(departure_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                        formatted_time_departure = departure_date_time.strftime('%d/%m/%Y %H:%M')

                        service_date = datetime.strptime(post['departure_date'], '%Y-%m-%d')
                        if departure_date_time <= datetime.today():
                            error.update({
                                'departure_date': 'Date should be greater than Today!',
                                # 'departure_time': 'Departure Time is Incorrect!'
                            })
                        departure_date_time = formatted_time_departure  + ':00'
                        # departure_date_time = departure_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # departure_date_time = self.convert_local_time_to_utc(departure_date_time, post.get('timezone'))

                elif service_type_id.is_transit:
                    if post.get('arrival_date', False) and post.get('arrival_hours_id', False) and post.get('arrival_minutes_id', False):
                        arrival_date_time_str = post['arrival_date'] + ' ' + post['arrival_hours_id'] + ':' + post['arrival_minutes_id']
                        arrival_date_time = datetime.strptime(arrival_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                        formatted_time_transit_arrival = arrival_date_time.strftime('%d/%m/%Y %H:%M')
                        if arrival_date_time <= datetime.today():
                            error.update({
                                'arrival_date': 'Date should be greater than Today!',
                                # 'arrival_time': 'Arrival Time is Incorrect!'
                            })
                        service_date = datetime.strptime(post['arrival_date'], '%Y-%m-%d')
                        arrival_date_time = formatted_time_transit_arrival + ':00'
                        # arrival_date_time = arrival_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # arrival_date_time = self.convert_local_time_to_utc(arrival_date_time, post.get('timezone'))

                        if post.get('departure_date', False) and post.get('departure_hours_id', False) and post.get('departure_minutes_id', False):
                            departure_date_time_str = post['departure_date'] + ' ' + post['departure_hours_id'] + ':' + \
                                                  post['departure_minutes_id']
                            departure_date_time = datetime.strptime(departure_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                            formatted_time_transit_departure = departure_date_time.strftime('%d/%m/%Y %H:%M')
                            arrival_date_time_b_str = post['arrival_date'] + ' ' + post['arrival_hours_id'] + ':' + post[
                                'arrival_minutes_id']
                            arrival_date_time_b = datetime.strptime(arrival_date_time_b_str, DEFAULT_FACTURX_DATE_FORMAT)
                            if departure_date_time <= datetime.today():
                                error.update({
                                    'departure_date': 'Date should be greater than Today!',
                                    # 'departure_time': 'Departure Time is Incorrect!'
                                })
                            elif departure_date_time < arrival_date_time_b:
                                error.update({
                                    'departure_date': 'Date should be greater than Arrival Date!',
                                    # 'departure_time': 'Departure Time is Incorrect!'
                                })
                            departure_date_time = formatted_time_transit_departure  + ':00'
                            # departure_date_time = departure_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            # departure_date_time = self.convert_local_time_to_utc(departure_date_time, post.get('timezone'))

            if error:
                values.update(post)
                values.update({
                    # 'services_ids': services,
                    'country_id': post.get('country_id') and int(post.get('country_id')) or False,
                    'airport_name': post.get('airport_id') and int(post.get('airport_id')) or '',
                    'service_types': post.get('service_types') and int(post.get('service_types')) or False,
                })
                if service_type_id:
                    if service_type_id.is_arrival:
                        values.update({
                            'service_types_name': 'arrival'
                        })
                    elif service_type_id.is_departure:
                        values.update({
                            'service_types_name': 'departure'
                        })
                    elif service_type_id.is_transit:
                        values.update({
                            'service_types_name': 'transit'
                        })
            else:
                vals = {
                    'uaa_services_id': request.env.ref("sr_uaa_main.airport_hotel_services").sudo().id,
                    'airport_id': post.get('airport_id') and int(post.get('airport_id')) or '',
                    'traveler_name': post.get('traveler_name') or '',
                    'email': post.get('email') or '',
                    'contact_number': post.get('contact_number') or '',
                    'country_id': post.get('country_id') and int(post.get('country_id')) or False,
                    'service_type_id': post.get('service_types') and int(post.get('service_types')) or False,
                    # 'services_ids': [(6, 0, services)],
                    'arrival_flight_number': post.get('arrival_flight_number') or '',
                    'arrival_date_str': arrival_date_time or False,
                    'departure_flight_number': post.get('departure_flight_number') or '',
                    'departure_date_str': departure_date_time or False,
                    'hours_count': post.get('hours_count') or '',
                    'service_date': service_date or False,
                    'adults_count': post.get('travelers_count') or '',
                    'customer_message': post.get('customer_message') or '',
                    'created_timezone': post.get('timezone') or request.env.context.get("tz") or request.env.user.tz or "UTC",
                }
                airport = request.env['airport.enquiry'].sudo().create(vals)
                success = True
                booking_ref = airport.name

        values.update({
            'error': error,
            'success': success,
            'booking_ref': booking_ref,
            'uaa_services': uaa_services,
            'service_type_ids': service_type_ids,
            'travel_class_ids': travel_class_ids,
            'booking_success_complete': request.env.ref("sr_uaa_main.uaa_booking_success_message").sudo().body

        })
        return request.render('sr_uaa_main.request_airport_hotel_page', values)
