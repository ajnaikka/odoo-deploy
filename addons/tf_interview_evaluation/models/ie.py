from odoo import models, fields, api,_

class InterviewEvaluvations(models.Model):
    _name = 'interview.evaluvations'
    _description = 'Interview Evaluvations'
    _order = 'id desc'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    candidate_name = fields.Char(string='Candidate Name')
    Position = fields.Char(string='Job Position for:')
    line_ids = fields.One2many('interview.evaluvations.line', 'interview_id', string='Interview Details')
    applicant_id = fields.Many2one('hr.applicant',string='applicant')

    @api.model
    def default_get(self, fields):
        res = super(InterviewEvaluvations, self).default_get(fields)
        line_defaults = []
        # if high_rate:
        line_defaults.append((0, 0,
                              { 'comment': 'EDUCTION TRAINING AND PROFESSIONAL EXPERIENCE'}))
        # if medium_rate:
        line_defaults.append((0, 0,
                              {'comment': 'WORK EXPERIENCE'}))
        # if low_rate:
        line_defaults.append((0, 0,
                              {'comment': 'PRESENTATION AND MANNER'}))
        line_defaults.append((0, 0,
                              {'comment': 'ATTITUDE,STABILITY AND MATURITY'}))
        line_defaults.append((0, 0,
                              {'comment': 'COMMUNICATION SKILLS'}))
        line_defaults.append((0, 0,
                              {'comment': 'INTER PERSONAL SKILLS'}))
        line_defaults.append((0, 0,
                              {'comment': 'MOTIVATION AND AMBITION'}))
        line_defaults.append((0, 0,
                              {'comment': 'INTELIGENCE'}))
        line_defaults.append((0, 0,
                              {'comment': 'DIVERSIFIED INTEREST'}))
        line_defaults.append((0, 0,
                              {'comment': 'LEADERSHIP EXPERICE'}))


        res.update({
            'line_ids': line_defaults,
        })

        return res



class InterviewEvaluvationsLine(models.Model):
    _name = 'interview.evaluvations.line'

    interview_id = fields.Many2one('interview.evaluvations')
    comment = fields.Char(string="Rating")
    comment1 = fields.Text(string="Comment")
    high_rate = fields.Selection([
        ('5', '5'),
        ('4', '4')
        ],string='High')
    meadium_rate = fields.Selection([
        ('3', '3'),
        ('2', '2')
        ],string='Medium')
    low_rate =  fields.Selection([
        ('1', '1')
        ],string='Low')






class HrApplicant(models.Model):
    _inherit = 'hr.applicant'


    def evaluvation(self):
        evaluvation_record = self.env['interview.evaluvations'].create({
            'applicant_id': self.id,
            # Add other default values if needed
        })

        view_id = self.env.ref('tf_interview_evaluation.interview_evaluvations_form').id

        # Return an action to open the form view
        return {
            'type': 'ir.actions.act_window',
            'name': 'Interview Evaluation Form',
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'interview.evaluvations',
            'target': 'current',
            'res_id':  evaluvation_record.id,  # Pass the ID of the newly created record
            'context': {
                'default_applicant_id': self.id,
                'default_candidate_name': self.partner_name if self.partner_name else None,
                'default_Position': self.name,
            }
        }

    def smart_evaluation(self):
        self.ensure_one()
        all_child = self.with_context(active_test=False).search([('id', 'in', self.ids)])

        action = self.env["ir.actions.act_window"]._for_xml_id("tf_interview_evaluation.interview_evaluvations_action")
        action['domain'] = [
            ('applicant_id', 'in', all_child.ids)
        ]
        action['context'] = {'search_default_applicant_id': self.id}
        return action





