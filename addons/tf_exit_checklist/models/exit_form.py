from odoo import models, fields, api,_
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)
import os

import base64

class ExitForm(models.Model):
    _name = 'exit.form'
    _description = 'Exit Form'
    _order = 'id desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    department_id = fields.Many2one('hr.department',string='Department')
    employee_id = fields.Many2one('hr.employee',string='Employee')
    date = fields.Date(string='Date',format='%d-%m-%y')
    # job_title = fields.
    Joining_date = fields.Date(string='Joining Date', format='%d-%m-%y')
    end_of_service_date = fields.Date(string='End of service Date',format='%d-%m-%y')
    exit_ids = fields.One2many('exit.form.line','exit_id',string='To department Manager')
    finance_ids = fields.One2many('finance.form.line','finance_id',string='To Finance Manager')
    # clearence_ids = fields.One2many('clearence.form.line','clearence_id',string='Clearence Form')
    total_accural = fields.Float(string='Total Accrual')
    total_deduction = fields.Float(string='Total Deduction')
    attach = fields.Binary('Document', copy=False)
    attachment = fields.Binary('Document', copy=False)
    is_approved = fields.Boolean(string='Approve')
    is_approve = fields.Boolean(string='Approve')
    is_iqama = fields.Boolean(string='Iqama in case of final exit')
    is_medical_insurance = fields.Boolean(string='Medical Insurance for employee and his/her family')
    is_business_card = fields.Boolean(string='Employees business card')
    is_identity_card = fields.Boolean(string='Company identity card')
    is_sponsership_transfer = fields.Boolean(string='Sponsership transfer undertaking in case of company acceptance')
    is_other_documents = fields.Boolean(string='Any other documents')
    it_status = fields.Selection([('yes', 'Yes'),
                                  ('no','No')
    ],string='Is the employee Cleared from IT Department')
    it_comment = fields.Text(string='Comments')
    finance_status = fields.Selection([('yes', 'Yes'),
                                  ('no', 'No')
                                  ],string='Is the employee Cleared from Finance Department')
    finance_comment = fields.Text(string='Comments')
    department_status = fields.Selection([('yes', 'Yes'),
                                  ('no', 'No')
                                  ],string='Is the employee Cleared from Department')
    department_comment = fields.Text(string='Comments')

    hr_status = fields.Selection([('yes', 'Yes'),
                                  ('no', 'No')
                                  ],string='Is the employee Cleared from Hr and Admin Department')
    hr_comment = fields.Text(string='Comments')
    clearence_status = fields.Selection([('cleared', 'Cleared'),
                                  ('not_cleared', 'Not Cleared')], string='Clearence Status')
    business_unit = fields.Char(string='Business unit/Location')
    attachment2 = fields.Binary('Document', copy=False)
    comments_by_hr = fields.Text(string='Comment by HR & Admin Manager')
    is_travel = fields.Boolean(string='Travel Agent')
    is_dpt = fields.Boolean(string='Department')
    is_Fin = fields.Boolean(string='Finance')
    @api.model
    def default_get(self, fields):
        res = super(ExitForm, self).default_get(fields)
        line_defaults = []
        # if high_rate:
        line_defaults.append((0, 0,
                              {'non_returnable_items': 'Salaries'}))
        # if medium_rate:
        line_defaults.append((0, 0,
                              {'non_returnable_items': 'Overtime(Hours)'}))
        # if low_rate:
        line_defaults.append((0, 0,
                              {'non_returnable_items': 'Annual Vacation'}))
        line_defaults.append((0, 0,
                              {'non_returnable_items': 'End of sevice compensation'}))
        line_defaults.append((0, 0,
                              {'non_returnable_items': 'Any other'}))


        res.update({
            'finance_ids': line_defaults,
        })

        return res

    @api.onchange('employee_id')
    def on_employee_id(self):
        if self.employee_id:
           self.department_id = self.employee_id.department_id.id
    def get_record_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&view_type=form&model={self._name}"

    def send_to_department(self):
        self.is_dpt = True
        mail_to_travelagent = self.env['mail.travelagent'].create({
            'exit_id': self.id,
        })

        view_id = self.env.ref('tf_exit_checklist.mail_travelagent_form').id

        # Return an action to open the form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clearence mail to Travel Agent',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'mail.travelagent',
            'target': 'current',
            'res_id': mail_to_travelagent.id,  # Pass the ID of the newly created record
            'context': {
                'default_exit_id': self.id,
                'default_is_department': True,
            }
        }


    def send_to_finance(self):
        self.is_Fin == True

        mail_to_travelagent = self.env['mail.travelagent'].create({
            'exit_id': self.id,
        })

        view_id = self.env.ref('tf_exit_checklist.mail_travelagent_form').id

        # Return an action to open the form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clearence mail to Travel Agent',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'mail.travelagent',
            'target': 'current',
            'res_id': mail_to_travelagent.id,  # Pass the ID of the newly created record
            'context': {
                'default_exit_id': self.id,
                'default_is_Finance': True,
            }
        }


    def send_to_travel_agent(self):
        self.is_travel = True
        mail_to_travelagent = self.env['mail.travelagent'].create({
            'exit_id': self.id,
            })

        view_id = self.env.ref('tf_exit_checklist.mail_travelagent_form').id

        # Return an action to open the form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Clearence mail to Travel Agent',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'mail.travelagent',
            'target': 'current',
            'res_id': mail_to_travelagent.id,  # Pass the ID of the newly created record
            'context': {
                'default_exit_id': self.id,
            }
        }


class ExitFormLine(models.Model):
    _name = 'exit.form.line'

    exit_id = fields.Many2one('exit.form')
    non_returnable_item = fields.Char(string='Non Returnable Items')
    Quantity = fields.Float(string='Non Returnable Items')
    Value = fields.Char(string='Value')
    # attach = fields.Binary('Document', copy=False)
class FinanceFormLine(models.Model):
    _name = 'finance.form.line'

    finance_id = fields.Many2one('exit.form')
    non_returnable_items = fields.Char(string='Accural')
    qty = fields.Float(string='Value')
    values = fields.Char(string='Deduction')
    value1 = fields.Float(string='Value')
class EmployeeForm(models.Model):
    _inherit = 'hr.employee'

    def action_send_exit_form(self):
        exit_record = self.env['exit.form'].create({
            'employee_id': self.id,
            # Add other default values if needed
        })

        view_id = self.env.ref('tf_exit_checklist.exit_form').id


        # Return an action to open the form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Exit Form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'exit.form',
            'target': 'current',
            'res_id':  exit_record.id,  # Pass the ID of the newly created record
            'context': {
                 'default_employee_id': self.id,
            }
        }

    # def smart_exit(self):
    #     self.ensure_one()
    #     all_child = self.with_context(active_test=False).search([('id', 'in', self.ids)])
    #
    #     action = self.env["ir.actions.act_window"]._for_xml_id("tf_exit_checklist.exit_form_action")
    #     action['domain'] = [
    #         ('employee_id', 'in', all_child.ids)
    #     ]
    #     action['context'] = {'search_default_employee_id': self.id}
    #     return action


