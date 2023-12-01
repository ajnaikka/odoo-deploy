# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import base64

from odoo import http
from odoo.addons.web.controllers.main import Session  # Import the class

import logging

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


class UniversalAirport(http.Controller):
    @http.route('/add_meet_greet', auth='user', type="json", methods=['POST'])
    def AddMeetandGreet(self, **kw):
        try:
            service_details = kw.get('service_details')
            airport_details = kw.get('airport_details')
            personal_details = kw.get('personal_details')
            flight_details = kw.get('flight_details')
            passenger_details = kw.get('passenger_details')
            airport = request.env['admin.airport'].sudo().browse(airport_details.get('id'))
            service_type = service_details.get('service_type')
            if service_type == 1:
                types = request.env['airport.service.type'].sudo().search([("is_arrival", "=", True)])
            elif service_type == 2:
                types = request.env['airport.service.type'].sudo().search([("is_departure", "=", True)])
            elif service_type == 3:
                types = request.env['airport.service.type'].sudo().search([("is_transit", "=", True)])
            else:
                types = False
            uaa_services_id = request.env['uaa.services'].sudo().search([("is_meet", "=", True)])
            country_id = request.env['res.country'].sudo().browse(int(passenger_details.get('country')))

            services = service_details.get('selected_service')
            list_service = []
            for serv in services:
                list_service.append(serv.get("id"))
            vals = {
                "uaa_services_id": uaa_services_id.id,
                "airport_id": airport.id if airport else False,
                "traveler_name": personal_details.get("name"),
                "email": personal_details.get("email"),
                "contact_number": personal_details.get("phone_number"),
                "arrival_flight_number": flight_details.get("flight_number"),
                "arrival_date_str": flight_details.get("arrival_date"),
                "arrival_date": flight_details.get("arrival_date"),
                "adults_count": passenger_details.get('adults_count'),
                "children_count": passenger_details.get('children_count'),
                "infants_count": passenger_details.get('infant_count'),
                "luggage_count": passenger_details.get('luggage_count'),
                "travel_class_id": service_details.get('class_of_travel'),
                "service_date": service_details.get("service_date"),
                "customer_message": service_details.get("message"),
                "service_type_id": types.id,
                "services_ids": [(6, 0, list_service)],
                "country_id": country_id.id
            }
            if vals:
                meet_greet = request.env['airport.enquiry'].sudo().create(vals)
                if meet_greet:
                    return_msg = {"success": True,
                                  "status": 200,
                                  "message": "Form submitted successfully",
                                  "booking_details": {
                                      "ref_number": meet_greet.name,
                                      "message": "Thank you for your enquiry",
                                  },
                                  "metadata": {}
                                  }
                    return return_msg
        except Exception as e:
            return_msg = {"success": False,
                          "status": 400,
                          "message": str(e),
                          "booking_details": {},
                          "metadata": {}
                          }
            return return_msg

    @http.route('/add_airport_transfer', auth='user', type="json", methods=['POST'])
    def AddAirportTransfer(self, **kw):
        try:
            service_details = kw.get('service_details')
            airport_details = kw.get('airport_details')
            personal_details = kw.get('personal_details')
            flight_details = kw.get('flight_details')
            passenger_details = kw.get('passenger_details')
            airport = request.env['admin.airport'].sudo().browse(airport_details.get('id'))
            service_type = service_details.get('service_type')
            if service_type == 1:
                types = request.env['airport.service.type'].sudo().search([("is_arrival", "=", True)])
            elif service_type == 2:
                types = request.env['airport.service.type'].sudo().search([("is_departure", "=", True)])
            elif service_type == 3:
                types = request.env['airport.service.type'].sudo().search([("is_transit", "=", True)])
            else:
                types = False
            uaa_services_id = request.env['uaa.services'].sudo().search([("is_airport_transfer", "=", True)])
            country_id = request.env['res.country'].sudo().browse(int(passenger_details.get('country')))

            services = service_details.get('selected_service')
            list_service = []
            for serv in services:
                list_service.append(serv.get("id"))

            pickup_airport = request.env['admin.airport'].sudo().browse(service_details.get('pick_up_location'))
            vals = {
                "uaa_services_id": uaa_services_id.id,
                "airport_id": airport.id if airport else False,
                "traveler_name": personal_details.get("name"),
                "email": personal_details.get("email"),
                "contact_number": personal_details.get("phone_number"),
                "arrival_flight_number": flight_details.get("flight_number"),
                "arrival_date_str": flight_details.get("arrival_date"),
                "arrival_date": flight_details.get("arrival_date"),
                "luggage_count": passenger_details.get('luggage_count'),
                "travel_class_id": service_details.get('class_of_travel'),
                "service_date": service_details.get("service_date"),
                "customer_message": service_details.get("message"),
                "service_type_id": types.id,
                "services_ids": [(6, 0, list_service)],
                "pick_up_airport_id": pickup_airport.id if pickup_airport else False,
                "drop_off_location": service_details.get('drop_off_location'),
                "country_id": country_id.id
            }
            if vals:
                transfer = request.env['airport.enquiry'].sudo().create(vals)
                if transfer:
                    return_msg = {"success": True,
                                  "status": 200,
                                  "message": "Form submitted successfully",
                                  "booking_details": {
                                      "ref_number": transfer.name,
                                      "message": "Thank you for your enquiry",
                                  },
                                  "metadata": {}
                                  }
                    return return_msg
        except Exception as e:
            return_msg = {"success": False,
                          "status": 400,
                          "message": str(e),
                          "booking_details": {},
                          "metadata": {}
                          }
            return return_msg

    @http.route('/add_airport_lounge', auth='user', type="json", methods=['POST'])
    def AddAirportLounge(self, **kw):
        try:
            service_details = kw.get('service_details')
            airport_details = kw.get('airport_details')
            personal_details = kw.get('personal_details')
            flight_details = kw.get('flight_details')
            passenger_details = kw.get('passenger_details')
            airport = request.env['admin.airport'].sudo().browse(airport_details.get('id'))
            service_type = service_details.get('service_type')
            if service_type == 1:
                types = request.env['airport.service.type'].sudo().search([("is_arrival", "=", True)])
            elif service_type == 2:
                types = request.env['airport.service.type'].sudo().search([("is_departure", "=", True)])
            elif service_type == 3:
                types = request.env['airport.service.type'].sudo().search([("is_transit", "=", True)])
            else:
                types = False
            uaa_services_id = request.env['uaa.services'].sudo().search([("is_airport_lounge", "=", True)])
            country_id = request.env['res.country'].sudo().browse(int(passenger_details.get('country')))

            services = service_details.get('selected_service')
            list_service = []
            for serv in services:
                list_service.append(serv.get("id"))
            vals = {
                "uaa_services_id": uaa_services_id.id,
                "airport_id": airport.id if airport else False,
                "traveler_name": personal_details.get("name"),
                "email": personal_details.get("email"),
                "contact_number": personal_details.get("phone_number"),
                "arrival_flight_number": flight_details.get("flight_number"),
                "arrival_date_str": flight_details.get("arrival_date"),
                "arrival_date": flight_details.get("arrival_date"),
                "travel_class_id": service_details.get('class_of_travel'),
                "service_date": service_details.get("service_date"),
                "customer_message": service_details.get("message"),
                "service_type_id": types.id,
                "services_ids": [(6, 0, list_service)],
                "hours_count": service_details.get('num_of_hours_of_stay'),
                "country_id": country_id.id
            }
            if vals:
                lounge = request.env['airport.enquiry'].sudo().create(vals)
                if lounge:
                    return_msg = {"success": True,
                                  "status": 200,
                                  "message": "Form submitted successfully",
                                  "booking_details": {
                                      "ref_number": lounge.name,
                                      "message": "Thank you for your enquiry",
                                  },
                                  "metadata": {}
                                  }
                    return return_msg
        except Exception as e:
            return_msg = {"success": False,
                          "status": 400,
                          "message": str(e),
                          "booking_details": {},
                          "metadata": {}
                          }
            return return_msg

    @http.route('/add_airport_hotel', auth='user', type="json", methods=['POST'])
    def AddAirportHotel(self, **kw):
        print("yesss", kw)
        try:
            service_details = kw.get('service_details')
            airport_details = kw.get('airport_details')
            personal_details = kw.get('personal_details')
            flight_details = kw.get('flight_details')
            passenger_details = kw.get('passenger_details')
            airport = request.env['admin.airport'].sudo().browse(airport_details.get('id'))
            service_type = service_details.get('service_type')
            if service_type == 1:
                types = request.env['airport.service.type'].sudo().search([("is_arrival", "=", True)])
            elif service_type == 2:
                types = request.env['airport.service.type'].sudo().search([("is_departure", "=", True)])
            elif service_type == 3:
                types = request.env['airport.service.type'].sudo().search([("is_transit", "=", True)])
            else:
                types = False
            uaa_services_id = request.env['uaa.services'].sudo().search([("is_airport_hotel", "=", True)])
            country_id = request.env['res.country'].sudo().browse(int(passenger_details.get('country')))

            services = service_details.get('selected_service')
            list_service = []
            for serv in services:
                list_service.append(serv.get("id"))
            vals = {
                "uaa_services_id": uaa_services_id.id,
                "airport_id": airport.id if airport else False,
                "traveler_name": personal_details.get("name"),
                "email": personal_details.get("email"),
                "contact_number": personal_details.get("phone_number"),
                "arrival_flight_number": flight_details.get("flight_number"),
                "arrival_date_str": flight_details.get("arrival_date"),
                "arrival_date": flight_details.get("arrival_date"),
                "adults_count": passenger_details.get('adults_count'),
                "children_count": passenger_details.get('children_count'),
                "infants_count": passenger_details.get('infant_count'),
                "luggage_count": passenger_details.get('luggage_count'),
                "travel_class_id": service_details.get('class_of_travel'),
                "service_date": service_details.get("service_date"),
                "customer_message": service_details.get("message"),
                "service_type_id": types.id,
                "services_ids": [(6, 0, list_service)],
                "country_id": country_id.id
            }
            if vals:
                hotel = request.env['airport.enquiry'].sudo().create(vals)
                if hotel:
                    return_msg = {"success": True,
                                  "status": 200,
                                  "message": "Form submitted successfully",
                                  "booking_details": {
                                      "ref_number": hotel.name,
                                      "message": "Thank you for your enquiry",
                                  },
                                  "metadata": {}
                                  }
                    return return_msg
        except Exception as e:
            return_msg = {"success": False,
                          "status": 400,
                          "message": str(e),
                          "booking_details": {},
                          "metadata": {}
                          }
            return return_msg