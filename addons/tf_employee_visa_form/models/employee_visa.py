from odoo import fields, models,api,_


class EmployeeVisa(models.Model):
    _name = 'employee.visa.form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Employee Visa Form'
    _rec_name= 'related_emp_id'

    applicant_name = fields.Char(string="Applicant Name",required=True)
    relation = fields.Char(string="Relation",required=True)
    emp_id = fields.Char(string="Employee Id")
    inv_letter = fields.Binary(string="Invitation Letter")
    file_name = fields.Char()
    state = fields.Selection([
        ('req', 'Request'),
        ('app_1', 'Approve 1'),
        ('app_2', 'Approve 2'),
        ('app_3', 'Approve 3'),
        ('done', 'Issued'),
        ('cancel', 'Rejected'),
    ],default='req', string='State')

    related_emp_id = fields.Many2one('hr.employee',string="Employee")
    user_id = fields.Many2one('res.users',default=lambda self:self.env.user)
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)

    # def get_url(self):
    #     base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    #     db_name = self.env.cr.dbname
    #     base_url += f'/web/login?db={db_name}#id=%d&view_type=form&model=%s' % (self.id, self._name)
    #     return base_url


    def action_send_mail(self, ctx=None):
        self.ensure_one()
        template = self.env.ref('tf_employee_visa_form.visa_application_email_id')

        attachment_data = {
            'name': 'Visa Application Letter',
            'datas': self.inv_letter,
            'res_model': self._name,
            'res_id': self.id,
        }

        attachment = self.env['ir.attachment'].create(attachment_data) if attachment_data.get('datas') else False

        context = {
            'default_model': 'employee.visa.form',
            'default_res_ids': self.ids,
            'default_partner_ids':[self.related_emp_id.parent_id.user_partner_id.id],
            'default_emp_visa_id': self.id,
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, [attachment.id])] if attachment else None,
            'force_email': True,
            'default_emp_send_mail': False,
            'default_partner_id':self.related_emp_id.parent_id.user_partner_id.id
        }

        if ctx:
            context.update(ctx)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': context,
        }

    def action_first_approval(self):
        return self.action_send_mail({'default_emp_send_mail': True})

    def action_final_approval(self):
        return self.action_send_mail({'default_emp_send_mail': True})

    def action_second_approval(self):
        return self.action_send_mail({'default_emp_send_mail': True})

    def action_third_approval(self):
        return self.action_send_mail({'default_emp_send_mail': True})

    def action_reject_1(self):
        return self.action_send_mail({'default_partner_ids':[self.env.user.partner_id.id],'default_body':None,'default_emp_reject_mail':True})

    def action_reject_2(self):
        return self.action_send_mail({'default_partner_ids':[self.env.user.partner_id.id],'default_emp_reject_mail':True,'default_body':None})

    def action_reject_3(self):
        return self.action_send_mail(({'default_partner_ids':[self.env.user.partner_id.id],'default_emp_reject_mail':True,'default_body':None}))







