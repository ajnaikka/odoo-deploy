# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 seeroo IT SOLUTIONS PVT.LTD(<http://www.seeroo.com>)
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
{
    'name': 'UAA Backend Main',
    'version': '1.1',
    'category': 'Website/Website',
    'summary': 'Module that contains core configurations for UAA project.',
    'description': """Module that contains core configurations for UAA project.""",
    'depends': ['base',
                'contacts',
                'sale_management',
                'account',
                'l10n_us',
                'payment',
                'mail'
                ],
    'data': [
        'security/security.xml',

        'security/ir.model.access.csv',
        'static/src/xml/template.xml',
        'static/src/xml/meet_greet_template.xml',
        'static/src/xml/airport_hotel_view.xml',
        'static/src/xml/airport_lounge_view.xml',
        'static/src/xml/airport_transfer.xml',
        'static/src/xml/payment_portal_templates.xml',
        'static/src/xml/payment_template.xml',
        'data/response_status.xml',
        'data/booking_sequence.xml',
        'data/service_name.xml',
        'data/airport_services.xml',
        'data/travel_class.xml',

        'data/uaa_mail_body.xml',
        'data/sale_mail_data.xml',
        'report/aditional_charge_template.xml',
        'data/mail_template.xml',
        'data/order_expiry_cron.xml',
        'data/enquiry_reminder_cron.xml',
        'data/enquiry_expiry_cron.xml',
        'data/enquiry_details_cron.xml',
        'data/enquiry_close_cron.xml',

        'report/payment_receipt_template.xml',
        'report/payment_transaction_template.xml',
        'report/booking_confirm_template.xml',
        'report/invoice_template.xml',
        'report/quotation_template.xml',
        'report/layout.xml',

        'wizards/enquiry_import.xml',
        'wizards/enquiry_warning.xml',
        'wizards/payment_dwld_wiz.xml',
        'wizards/cancel_enquiry_wiz.xml',
        'wizards/close_enquiry_wiz.xml',
        'wizards/additional_charge_wiz.xml',

        'views/admin_airport.xml',
        'views/airport_enquiry.xml',
        'views/service_name.xml',
        'views/res_partner.xml',
        'views/product_view.xml',
        'views/sale_order_view.xml',
        'views/report_view.xml',
        'views/bank.xml',
        'views/service_category.xml',
        'views/airport_service.xml',
        'views/account_move_view.xml',
        'views/enquiry_service_line.xml',
        'views/service_line_views.xml',
        'views/airport_service_type.xml',
        'views/travel_class_views.xml',
        'views/response_status.xml',
        'views/enquiry_status.xml',
        'views/company_view.xml',
        'views/uaa_mail_body.xml',
        'views/res_config_settings.xml',
        'views/additional_charge.xml',
        'views/payment_templates.xml',
        # 'views/payment_confirm.xml',

        'views/menu.xml',
    ],
    'qweb': [
        # 'static/src/xml/template.xml',

    ],
    'installable': True,
    'auto_install': False,
    'author': 'Seeroo IT Solutions',
    'website': 'https://www.seeroo.com',
}
