from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_term_ids = fields.One2many('employee.termination','related_emp_con_id')
    age = fields.Integer(string="Age",compute="_compute_age",store=True)

    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            if rec.birthday:
                today = fields.Date.today()
                birthdate = fields.Date.from_string(rec.birthday)
                age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
                rec.age = age
            else:
                rec.age = 0



    def action_emp_termination_form(self):

        action = {
            'name': 'Employee Termination',
            'type': 'ir.actions.act_window',
            'res_model': 'employee.termination',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_related_emp_con_id': self.id},

        }

        return action