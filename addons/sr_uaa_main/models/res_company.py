# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    booking_footer_text = fields.Text('Booking Report Footer')
    booking_confirmation_text = fields.Text('Booking Confirmation Body')
    terms_conditions = fields.Text('Terms & Conditions')
    cancellation_policy = fields.Text('Cancellation Policy')
    booking_email = fields.Char(string='Booking Email',)
    booking_cc = fields.Char(string='Booking CC Emails',)
    payment_response_mail = fields.Char(string='Payment Response Emails',)
    default_sale_order_validity_hours = fields.Integer(
        string="Default Validity of Quotation",
        help="By default, the validity date of Quotation will be "
             "the date of the sale order plus 24 Hours defined "
             "in this field. If the value of this field is 0, the Quotation "
             "will not have a validity date by default.",
    )

    _sql_constraints = [
        (
            "sale_order_validity_hours_positive",
            "CHECK (default_sale_order_validity_hours >= 0)",
            "The value of the field 'Default Validity Duration of Quotation' "
            "must be positive or 0.",
        ),
    ]


