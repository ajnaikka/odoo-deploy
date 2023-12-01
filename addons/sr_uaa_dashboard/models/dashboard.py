from odoo import models, fields, api
from odoo.http import request
import datetime


class UAADashboard(models.Model):
    _name = 'uaa.dashboard'
    _description = 'UAA Landscape Dashboard'

    @api.model
    def get_info(self):
        uid = request.session.uid
        EnquiryPool = self.env['airport.enquiry'].sudo()
        user_id = self.env['res.users'].sudo().browse(uid)
        my_customers = self.env['res.partner'].sudo().\
            search([('company_type','=','person'),('company_name','=',False)])
        my_airports = self.env['admin.airport'].sudo().search([])
        my_enquires = EnquiryPool.search([])
        my_upcoming_services = EnquiryPool.search(
            [('service_date', '>=', fields.Date.today()), 
             ('payment_done', '=', True), 
             ('response_status','=','confirmation_voucher_send'),
             ('status', '=', 'open')])
        my_new_enquires = EnquiryPool.search([('status','=','new')])
        my_open_enquires = EnquiryPool.search([('status','=','open')])
        my_close_enquires = EnquiryPool.search([('status', '=', 'close')])
        my_cancelled_enquires = EnquiryPool.search([('response_status', '=', 'cancelled')])
        my_payment_completed_enquires = EnquiryPool.search([('payment_status', '=', 'paid'),
                                                            ('status', '!=', 'close')])
        dashboard_details = [{}]
        data = {
            'user_id': user_id.id,
            'user': user_id,
            'my_new_enquires': len(my_new_enquires),
            'my_customers': len(my_customers),
            # 'my_upcoming_enquires': len(my_upcoming_enquires),
            'my_upcoming_services': len(my_upcoming_services),
            'my_open_enquires': len(my_open_enquires),
            'my_close_enquires': len(my_close_enquires),
            'my_cancelled_enquires': len(my_cancelled_enquires),
            'my_paid_enquires': len(my_payment_completed_enquires),
            'my_enquires': len(my_enquires),
            'my_airports': len(my_airports),
        }
        dashboard_details[0].update(data)
        return dashboard_details