# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class ProductProduct(models.Model):
    _inherit = 'product.template'
    expiry_date = fields.Date(string='Expiry Date', copy=False,
                              help="Date of expiry")

    noti_on_expiry_day = fields.Boolean('Notification on Expiry day', default=True)
    noti_before_three_month = fields.Boolean('Notification before 3 months', default=True)
    noti_before_six_month = fields.Boolean('Notification before 6 months', default=True)
    noti_before_1_year = fields.Boolean('Notification before 1 year', default=True)

    three_month = fields.Integer(compute='_compute_three_month')

    def _compute_three_month(self):

        self.three_month = 30

    six_month = fields.Integer(compute='_compute_six_month')

    def _compute_six_month(self):

        self.six_month = 60

    one_year = fields.Integer(compute='_compute_one_year')

    def _compute_one_year(self):

        self.one_year = 365

    @api.constrains('expiry_date')
    def check_expr_date(self):
        for each in self:
            if each.expiry_date:
                exp_date = fields.Date.from_string(each.expiry_date)
                if exp_date < date.today():
                    raise Warning('Your Product Is Expired.')

    def mail_reminder(self):
        """Sending document expiry notification to Inventory user."""

        date_now = fields.Date.today()
        match = self.search([])
        users = self.env['res.users'].sudo().search([])
        for partner in self.env['res.users'].search([('notify_expiry_user', "=", True)]):
            if partner.notify_expiry_user:
                for i in match:
                    if i.expiry_date:
                        if i.branch_id.id in partner.branch_ids.ids:
                            if i.noti_on_expiry_day == True:
                                exp_date = fields.Date.from_string(i.expiry_date)
                                if date_now == i.expiry_date:
                                    mail_content = "  Hello  " + partner.name + ",<br>Your Product " + i.name + " is expired on " + \
                                                   str(i.expiry_date)
                                    main_content = {
                                        'subject': _('Product-%s Expired On %s') % (
                                            i.name, i.expiry_date),
                                        'author_id': self.env.user.partner_id.id,
                                        'body_html': mail_content,
                                        'email_to': partner.email,
                                        # 'email_to': self.env.user.partner_id.email,
                                    }
                                    self.env['mail.mail'].sudo().create(main_content).send()

                            if i.noti_before_three_month == True:
                                exp_date = fields.Date.from_string(
                                    i.expiry_date) - timedelta(days=i.three_month)
                                if date_now == exp_date or date_now == i.expiry_date:  # on Expire date and few days(As it set) before expire date
                                    mail_content = "  Hello  " + partner.name + ",<br>Your Product " + i.name + \
                                                   " is going to expire on " + str(
                                        i.expiry_date)
                                    main_content = {
                                        'subject': _('Product-%s Will Expire On %s') % (
                                            i.name, i.expiry_date),
                                        'author_id': self.env.user.partner_id.id,
                                        'body_html': mail_content,
                                        'email_to': partner.email,
                                    }
                                    self.env['mail.mail'].sudo().create(main_content).send()

                            if i.noti_before_six_month == True:
                                exp_date = fields.Date.from_string(
                                    i.expiry_date) - timedelta(days=i.six_month)
                                if date_now == exp_date or date_now == i.expiry_date:  # on Expire date and few days(As it set) before expire date
                                    mail_content = "  Hello  " + partner.name + ",<br>Your Product " + i.name + \
                                                   " is going to expire on " + str(
                                        i.expiry_date)
                                    main_content = {
                                        'subject': _('Product-%s Will Expire On %s') % (
                                            i.name, i.expiry_date),
                                        'author_id': self.env.user.partner_id.id,
                                        'body_html': mail_content,
                                        'email_to': partner.email,
                                    }
                                    self.env['mail.mail'].sudo().create(main_content).send()

                            if i.noti_before_1_year == True:
                                exp_date = fields.Date.from_string(
                                    i.expiry_date) - timedelta(days=i.one_year)
                                if date_now == exp_date or date_now == i.expiry_date:  # on Expire date and few days(As it set) before expire date
                                    mail_content = "  Hello  " + partner.name + ",<br>Your Product " + i.name + \
                                                   " is going to expire on " + str(
                                        i.expiry_date)
                                    main_content = {
                                        'subject': _('Product-%s Will Expire On %s') % (
                                            i.name, i.expiry_date),
                                        'author_id': self.env.user.partner_id.id,
                                        'body_html': mail_content,
                                        'email_to': partner.email,
                                    }
                                    self.env['mail.mail'].sudo().create(main_content).send()


class ResUsers(models.Model):
    _inherit = 'res.users'

    notify_expiry_user = fields.Boolean(string="Notify User For Product Expiry")
