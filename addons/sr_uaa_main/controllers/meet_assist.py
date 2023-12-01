from odoo import http
from odoo.http import request

import re
import pytz
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
Integerregex = r'^\d+$'
DEFAULT_FACTURX_DATE_FORMAT = '%Y-%m-%d %H:%M'
DEFAULT_FACTURE_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class MeetGreetServices(http.Controller):

    def checkString(self, str):
        flag_l = False
        flag_n = False
        for i in str:
            if i.isalpha():
                flag_l = True
            if i.isdigit():
                flag_n = True
        return (flag_l and flag_n)

    def convert_local_time_to_utc(self, date_str=False,
            timeZone = ""):
        if(not timeZone):
            timeZone = request.env.context.get("tz") or request.env.user.tz or "UTC"
        display_date_result = False
        if date_str:
            user_tz = pytz.timezone(timeZone)
            dateformat_obj = datetime.strptime(str(date_str), DEFAULT_FACTURE_DATE_FORMAT)
            date_start = user_tz.localize(dateformat_obj).astimezone(pytz.timezone("UTC"))
            display_date_result = date_start.strftime(DEFAULT_FACTURE_DATE_FORMAT)
        return display_date_result

    @http.route('/request-meet-greet', type='http', auth='public', website=True, methods=['GET', 'POST'], csrf=False)
    def request_meet_greet_details(self, **post):
        values = {}
        error = {}
        success = False
        booking_ref = False
        second_page = False
        uaa_services = request.env['uaa.services'].sudo().search([])
        airport_services = request.env['airport.service.name'].sudo().search([('show_meet_greet','=',True)])
        airports = request.env['admin.airport'].sudo().search([])
        countries = request.env['res.country'].sudo().search([])
        service_type_ids = request.env['airport.service.type'].sudo().search([])
        # service_type_ids = request.env.ref("sr_uaa_main.meet_greet_services").sudo().service_type_ids
        travel_class_ids = request.env['travel.class'].sudo().search([])
        title = request.env.ref("sr_uaa_main.meet_greet_services").sudo().name
        values.update({
            'title': title,
            'hours_id': '',
            'minutes_id': '',
            'service_types_name': 'arrival',
            'services': airport_services,
            'airports': airports,
            'countries': countries,
            'airport_name': '',
            'traveler_name': '',
            'email': '',
            'country_code': '',
            'mobile': '',
            'service_types': '',
            'services_ids': [],
            'arrival_flight_number': '',
            'departure_flight_number': '',
            'class_of_travel': '',
            'arrival_date': '',
            'departure_date': '',
            'departure_time': '',
            'children': '',
            'infants': '',
            'no_luggages': '',
            'wheel_chair': False,
            'coupon_code': '',
            'customer_message': '',
            'enqcaptcha': '',

        })
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
        if post and request.httprequest.method == 'POST':
            if not post.get('airport_name', False):
                error.update({
                    'airport_name': 'Airport Name is missing!'
                })
            if not post.get('traveler_name', False):
                error.update({
                    'traveler_name': 'Traveller Name is missing!'
                })
            if not post.get('email', False):
                error.update({
                    'email': 'Email Address is missing!'
                })
            elif not re.fullmatch(regex, post.get('email', False)):
                error.update({
                    'email': 'Please enter a valid Email Address!'
                })

            if not post.get('mobile', False):
                error.update({
                    'country_code': 'Contact Number is missing!',
                    'mobile': 'MISSING'
                })
            if not post.get('country_code', False):
                error.update({
                    'country_code': 'Country Code is missing!'
                })
                if not post.get('mobile', False):
                    error.update({
                        'country_code': 'Country Code and Contact Number is missing!',
                        'mobile': 'MISSING'
                    })
            if not post.get('service_types', False):
                second_page = True
                error.update({
                    'service_types': 'Service Type is missing!'
                })
                service_type_id = False
            else:
                service_type_id = request.env['airport.service.type'].sudo().browse(int(post.get('service_types')))
            if service_type_id:
                if service_type_id.is_arrival:
                    if not post.get('arrival_flight_number', False):
                        second_page = True
                        error.update({
                            'arrival_flight_number': 'Arrival Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('arrival_flight_number')):
                    #     second_page = True
                    #     error.update({
                    #         'arrival_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('arrival_date', False):
                        second_page = True
                        error.update({
                            'arrival_date': 'Arrival Date is missing!'
                        })
                    if not post.get('arrival_hours_id', False):
                        second_page = True
                        error.update({
                            'arrival_time': 'Hour is missing!'
                        })
                        if not post.get('arrival_minutes_id', False):
                            second_page = True
                            error.update({
                                'arrival_time': 'Arrival Time is missing!'
                            })
                    elif not post.get('arrival_minutes_id', False):
                        second_page = True
                        error.update({
                            'arrival_time': 'Minute is missing!'
                        })
                elif service_type_id.is_departure:
                    if not post.get('departure_flight_number', False):
                        second_page = True
                        error.update({
                            'departure_flight_number': 'Departure Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('departure_flight_number')):
                    #     second_page = True
                    #     error.update({
                    #         'departure_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('departure_date', False):
                        second_page = True
                        error.update({
                            'departure_date': 'Departure Date is missing!'
                        })
                    if not post.get('departure_hours_id', False):
                        second_page = True
                        error.update({
                            'departure_time': 'Hour is missing!'
                        })
                        if not post.get('departure_minutes_id', False):
                            second_page = True
                            error.update({
                                'departure_time': 'Departure Time is missing!'
                            })
                    elif not post.get('departure_minutes_id', False):
                        second_page = True
                        error.update({
                            'departure_time': 'Minute is missing!'
                        })
                elif service_type_id.is_transit:
                    if not post.get('arrival_flight_number', False):
                        second_page = True
                        error.update({
                            'arrival_flight_number': 'Arrival Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('arrival_flight_number')):
                    #     second_page = True
                    #     error.update({
                    #         'arrival_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('arrival_date', False):
                        second_page = True
                        error.update({
                            'arrival_date': 'Arrival Date is missing!'
                        })
                    if not post.get('arrival_hours_id', False):
                        second_page = True
                        error.update({
                            'arrival_time': 'Hour is missing!'
                        })
                        if not post.get('arrival_minutes_id', False):
                            second_page = True
                            error.update({
                                'arrival_time': 'Arrival Time is missing!'
                            })
                    elif not post.get('arrival_minutes_id', False):
                        second_page = True
                        error.update({
                            'arrival_time': 'Minute is missing!'
                        })
                    if not post.get('departure_flight_number', False):
                        second_page = True
                        error.update({
                            'departure_flight_number': 'Departure Flight Number is missing!'
                        })
                    # elif not self.checkString(post.get('departure_flight_number')):
                    #     second_page = True
                    #     error.update({
                    #         'departure_flight_number': 'Invalid Flight Number!'
                    #     })
                    if not post.get('departure_date', False):
                        second_page = True
                        error.update({
                            'departure_date': 'Departure Date is missing!'
                        })
                    if not post.get('departure_hours_id', False):
                        second_page = True
                        error.update({
                            'departure_time': 'Hour is missing!'
                        })
                        if not post.get('departure_minutes_id', False):
                            second_page = True
                            error.update({
                                'departure_time': 'Departure Time is missing!'
                            })
                    elif not post.get('departure_minutes_id', False):
                        second_page = True
                        error.update({
                            'departure_time': 'Minute is missing!'
                        })

            if not post.get('class_of_travel', False):
                second_page = True
                error.update({
                    'class_of_travel': 'Class of travel is missing!'
                })
            # if not post.get('customer_message', False):
            #     second_page = True
            #     error.update({
            #         'customer_message': 'Message is missing!'
            #     })

            if post.get('adults', False):
                if not re.fullmatch(Integerregex, post.get('adults', False)):
                    second_page = True
                    error.update({
                        'adults': 'Value should be a positive number!'
                    })
            if not post.get('adults', False):
                second_page = True
                error.update({
                    'adults': 'No of adults is missing!'
                })
            if post.get('no_luggages', False):
                if not re.fullmatch(Integerregex, post.get('no_luggages', False)):
                    second_page = True
                    error.update({
                        'no_luggages': 'Value should be a positive number!'
                    })
            if not post.get('no_luggages', False):
                second_page = True
                error.update({
                    'no_luggages': 'No. of luggage is missing!'
                })

            if post.get('children', False):
                if not re.fullmatch(Integerregex, post.get('children', False)):
                    second_page = True
                    error.update({
                        'children': 'Value should be a positive number!'
                    })

            if post.get('infants', False):
                if not re.fullmatch(Integerregex, post.get('infants', False)):
                    second_page = True
                    error.update({
                        'infants': 'Value should be a positive number!'
                    })
            # if not post.get('enqcaptcha', False):
            #     error.update({
            #         'enqcaptcha': 'Captche is missing!'
            #     })
            services = []
            services_list = [key for key, v in post.items() if key.startswith('servicesinput_')]
            if services_list:
                for serv_list in services_list:
                    ser_id = int(serv_list.split('_')[1])
                    services.append(ser_id)
            if not services:
                second_page = True
                error.update({
                    'services': 'Services is missing!'
                })
            # if request.httprequest.form.getlist('services_ids'):
            #     for serv in request.httprequest.form.getlist('services_ids'):
            #         services.append(int(serv))
            arrival_date_time = False
            departure_date_time = False
            service_date = False
            if service_type_id:
                if service_type_id.is_arrival:
                    if post.get('arrival_date', False) and post.get('arrival_hours_id', False) and post.get('arrival_minutes_id', False):
                        arrival_date_time_str = post['arrival_date'] + ' ' + post['arrival_hours_id'] + ':' + post['arrival_minutes_id']
                        service_date = datetime.strptime(post['arrival_date'], '%Y-%m-%d')
                        arrival_date_time = datetime.strptime(arrival_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                        print("arrival_date_time", arrival_date_time)
                        formatted_time_arrival = arrival_date_time.strftime('%d/%m/%Y %H:%M')
                        print("formatted_time_arrival", formatted_time_arrival )


                        if arrival_date_time <= datetime.today():
                            second_page = True
                            error.update({
                                'arrival_date': 'Date should be greater than Today!',
                                'arrival_time': 'Arrival Time is Incorrect!'
                            })
                        arrival_date_time = formatted_time_arrival + ':00'
                        # arrival_date_time = arrival_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # arrival_date_time = self.convert_local_time_to_utc(arrival_date_time, post.get('timezone'))

                elif service_type_id.is_departure:
                    if post.get('departure_date', False) and post.get('departure_hours_id', False) and post.get('departure_minutes_id', False):
                        departure_date_time_str = post['departure_date'] + ' ' + post['departure_hours_id'] + ':' + post['departure_minutes_id']
                        service_date = datetime.strptime(post['departure_date'], '%Y-%m-%d')
                        departure_date_time = datetime.strptime(departure_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                        formatted_time_departure = departure_date_time.strftime('%d/%m/%Y %H:%M')
                        if departure_date_time <= datetime.today():
                            second_page = True
                            error.update({
                                'departure_date': 'Date should be greater than Today!',
                                # 'departure_time': 'Departure Time is Incorrect!'
                            })
                        departure_date_time = formatted_time_departure + ':00'
                        # departure_date_time = departure_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # departure_date_time = self.convert_local_time_to_utc(departure_date_time, post.get('timezone'))

                elif service_type_id.is_transit:
                    if post.get('arrival_date', False) and post.get('arrival_hours_id', False) and post.get('arrival_minutes_id', False):
                        arrival_date_time_str = post['arrival_date'] + ' ' + post['arrival_hours_id'] + ':' + post['arrival_minutes_id']
                        arrival_date_time = datetime.strptime(arrival_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                        formatted_time_transit_arrival = arrival_date_time.strftime('%d/%m/%Y %H:%M')
                        service_date = datetime.strptime(post['arrival_date'], '%Y-%m-%d')
                        if arrival_date_time <= datetime.today():
                            second_page = True
                            error.update({
                                'arrival_date': 'Date should be greater than Today!',
                                # 'arrival_time': 'Arrival Time is Incorrect!'
                            })
                        arrival_date_time = formatted_time_transit_arrival + ':00'
                        # arrival_date_time = arrival_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        # arrival_date_time = self.convert_local_time_to_utc(arrival_date_time, post.get('timezone'))

                        if post.get('departure_date', False) and post.get('departure_hours_id', False) and post.get('departure_minutes_id', False):
                            departure_date_time_str = post['departure_date'] + ' ' + post['departure_hours_id'] + ':' + post['departure_minutes_id']
                            departure_date_time = datetime.strptime(departure_date_time_str, DEFAULT_FACTURX_DATE_FORMAT)
                            arrival_date_time_a = post['arrival_date'] + ' ' + post['arrival_hours_id'] + ':' + post['arrival_minutes_id']
                            arrival_date_time_a = datetime.strptime(arrival_date_time_a, DEFAULT_FACTURX_DATE_FORMAT)
                            formatted_time_transit_departure = departure_date_time.strftime('%d/%m/%Y %H:%M')
                            if departure_date_time <= datetime.today():
                                second_page = True
                                error.update({
                                    'departure_date': 'Date should be greater than Today!',
                                })
                            elif departure_date_time < arrival_date_time_a:
                                second_page = True
                                error.update({
                                    'departure_date': 'Date should be greater than Arrival Date!',
                                })
                            departure_date_time = formatted_time_transit_departure + ':00'
                            # departure_date_time = departure_date_time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                            # departure_date_time = self.convert_local_time_to_utc(departure_date_time, post.get('timezone'))
            if error:
                values.update(post)
                values.update({
                    'services_ids': services,
                    'service_types': post.get('service_types', False) and int(post.get('service_types')) or False,
                    'country_code': post.get('country_code', False) and int(post.get('country_code')) or False,
                    'airport_name': post.get('airport_name', False) and int(post.get('airport_name')) or False,
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
                    'uaa_services_id': request.env.ref("sr_uaa_main.meet_greet_services").sudo().id,
                    'airport_id': post.get('airport_name') and int(post.get('airport_name')) or False,
                    'traveler_name': post.get('traveler_name', False),
                    'email': post.get('email', False),
                    'contact_number': post.get('mobile', False),
                    'country_id': post.get('country_code') and int(post.get('country_code')) or False,
                    'service_type_id': post.get('service_types') and int(post.get('service_types')) or False,
                    'services_ids': [(6, 0, services)],
                    'arrival_flight_number': post.get('arrival_flight_number') or '',
                    'arrival_date_str': arrival_date_time or False,
                    'departure_flight_number': post.get('departure_flight_number') or '',
                    'departure_date_str': departure_date_time or False,
                    'travel_class_id': post.get('class_of_travel') and int(post.get('class_of_travel')) or False,
                    'adults_count': post.get('adults', 0),
                    'children_count': post.get('children', 0),
                    'infants_count': post.get('infants', 0),
                    'luggage_count': post.get('no_luggages', 0),
                    'service_date': service_date or False,
                    'customer_message': post.get('customer_message') or '',
                    'created_timezone': post.get('timezone') or request.env.context.get(
                        "tz") or request.env.user.tz or "UTC",

                }
                if post.get('wheel_chair') == 'on':
                    vals.update({
                        'need_wheelchair': True,
                        'wheelchair_count': 1,
                    })
                airport = request.env['airport.enquiry'].sudo().create(vals)
                success = True
                booking_ref = airport.name
        values.update({
            'error': error,
            'success': success,
            'booking_ref': booking_ref,
            'second_page': second_page,
            'uaa_services': uaa_services,
            'service_type_ids': service_type_ids,
            'travel_class_ids': travel_class_ids,
            'booking_success_complete': request.env.ref("sr_uaa_main.uaa_booking_success_message").sudo().body
        })
        return request.render('sr_uaa_main.request_meet_greet_details_page', values)