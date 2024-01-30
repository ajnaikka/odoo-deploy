from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    visa_count = fields.Float(string="Visa",compute="_compute_visa_count")
    visa_app_ids = fields.One2many('employee.visa.form','related_emp_id')
    is_true = fields.Boolean(string="Is True")

    @api.onchange('marital')
    def onchange_marital(self):
        if self.marital == 'married':
            self.is_true = True
        else:
            self.is_true = False


    def _compute_visa_count(self):
        for rec in self:
            rec.visa_count = self.env['employee.visa.form'].search_count([('related_emp_id','=',self.id)])

    def action_view_visa_application(self):
        return {
            'name': 'Employee Visa',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.visa.form',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain':[('related_emp_id', '=', self.id)]
        }

    def action_visa_application_form(self):

        action = {
            'name': 'Employee Visa',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.visa.form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_emp_id': self.id},

        }

        return action