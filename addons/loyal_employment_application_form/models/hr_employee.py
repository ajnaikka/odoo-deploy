from odoo import models, fields, api


class EmployeeEducationalQualification(models.Model):
    _name = 'hr.employee.educational.qualification'
    _description = 'Employee Educational Qualification'

    name = fields.Char('Name of High School/University (City & Country)', required=True)
    years_from = fields.Date('From')
    years_to = fields.Date('To')
    languages = fields.Char('In what languages were your lessons taught?')
    certificates = fields.Char('Certificates Awarded')
    grade_point = fields.Float('Grade Points average')
    out_of = fields.Float('Out of possible')
    employee_id = fields.Many2one('hr.employee', string='Employee')


class EmployeeProfessionalQualification(models.Model):
    _name = 'hr.employee.professional.qualification'
    _description = 'Employee Professional Qualification'

    name_of_institution = fields.Char('Name of Professional Institute', required=True)
    qualification = fields.Char('Qualification Awarded')
    date = fields.Date('Date')
    class_of_membership = fields.Char('Class Of Membership')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)


class EmployeeOtherLanguages(models.Model):
    _name = 'hr.employee.other.languages'
    _description = 'Employee Other Languages'

    language = fields.Char('Language', required=True)
    spoken = fields.Char('Spoken')
    written = fields.Char('Written')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)


class EmployeeComputerSkills(models.Model):
    _name = 'hr.employee.computer.skills'
    _description = 'Employee Computer Skills'

    software = fields.Char('Software', required=True)
    very_good = fields.Integer('Very Good')
    good = fields.Integer('Good')
    fair = fields.Integer('Fair')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)


class EmployeePastEmployer(models.Model):
    _name = 'hr.employee.past.employer'
    _description = 'Employee Past Employer'

    name_of_employer = fields.Char('Name of employer')
    nature_of_business = fields.Char('Nature of business')
    postal_address = fields.Text('Postal address (Telephone & Fx numbers)')
    date_joined = fields.Text('Date joined & date left (Period of service)')
    job_title = fields.Char('Job title while joining')
    job_title_leaving = fields.Char('Job title while leaving')
    subordinates_job_title = fields.Text('Job titles of your subordinates (if any)')
    responsibilities = fields.Text('Brief Responsibilities')
    supervisor_name = fields.Text('Name and job title of your direct supervisor')
    reasons_for_leaving = fields.Text('Specify your reasons for leaving')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)


class EmployeeChecklistQuestions(models.Model):
    _name = 'hr.employee.checklist.questions'
    _description = 'Employee Checklist Questions'

    name = fields.Char('Question')


class EmployeeChecklist(models.Model):
    _name = 'hr.employee.checklist'
    _description = 'Employee Checklist'

    question_id = fields.Many2one('hr.employee.checklist.questions', 'Question', required=True)
    is_checked = fields.Boolean('Please Tick')
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _default_checklist(self):
        checklist_questions = self.env['hr.employee.checklist.questions'].search([])
        check_list = []
        for rec in checklist_questions:
            values = {}
            values['question_id'] = rec.id
            values['is_checked'] = False
            check_list.append((0, 0, values))
        return check_list

    # employment form fields
    pinfo_name = fields.Char('Name')
    pinfo_birthday = fields.Date('Date of Birth')
    pinfo_place_of_birth = fields.Char('Place of Birth')
    pinfo_marital_status = fields.Char('Marital Status')
    pinfo_country_id = fields.Many2one(
        'res.country', 'Nationality (Country)')
    pinfo_no_of_dependents = fields.Integer('No. of Children/Dependents')
    pinfo_mailing_address = fields.Text('Mailing Address (Current Location)')
    pinfo_email = fields.Char('Email')
    pinfo_telephone = fields.Char('Telephone No.')
    pinfo_fax_no = fields.Char('Fax No.')
    pinfo_mobile = fields.Char('Mobile No.')
    employee_education_ids = fields.One2many('hr.employee.educational.qualification', 'employee_id',
                                             'Educational Qualifications')
    professional_qualification_ids = fields.One2many('hr.employee.professional.qualification', 'employee_id',
                                                     'Professional Qualifications')
    mother_tongue = fields.Char('What is your mother tongue?')
    languages_ids = fields.One2many('hr.employee.other.languages', 'employee_id',
                                    'Other Languages')
    employee_computer_skills_ids = fields.One2many('hr.employee.computer.skills', 'employee_id',
                                                   'Computer Skills')
    condition_of_health = fields.Text('Condition Of Health')
    is_medication = fields.Boolean('Are you presently under any medication?')
    medication = fields.Text('If yes, please specify')
    operations = fields.Text('Operations')
    is_currently_employed = fields.Boolean('Are you currently employed?')
    work_start_date = fields.Date('Specify the date when you can start work at CT if a position is offered')
    career_objective = fields.Text('What are your career objectives over the next 3-6 years?')
    skills = fields.Text('What are the strength parts/skills that you find the most in yourself in your career?')
    development_areas = fields.Text(
        'What are the areas of development that you find the most in yourself in your career?')
    name_of_current_employer = fields.Char('Name of Current/ Last Employer')
    nature_of_business = fields.Char('Nature of business')
    postal_address = fields.Text('Postal address (Telephone & Fax numbers)')
    joined_date = fields.Char('Date of joined & date left (Period of service)')
    current_job_title = fields.Char('Your current/last job title')
    subordinates_job_titles = fields.Char('Job titles of your subordinates (if any)')
    supervisor_job_title = fields.Char('Name and job title of your direct supervisor')
    duties_and_responsibilities = fields.Text('Summarize your duties and responsibilities')
    leaving_reason = fields.Text('Specify your reasons for wanting to leave')
    current_monthly_salary = fields.Float('Current monthly salary')
    annual_compensation_package = fields.Char('Value of annual compensation package')
    required_annual_compensation = fields.Char('Specify value of annual compensation package required')
    past_employer_ids = fields.One2many('hr.employee.past.employer', 'employee_id',
                                        'Past Employer Details')
    previous_supervisor_name_1 = fields.Char('Name')
    previous_supervisor_address_1 = fields.Text('Address')
    previous_supervisor_tel_no_1 = fields.Text('Tel. No.')
    previous_supervisor_fax_1 = fields.Text('Fax/Email')
    previous_supervisor_fax_2 = fields.Text('Fax/Email')
    previous_supervisor_tel_no_2 = fields.Text('Tel. No.')
    previous_supervisor_address_2 = fields.Text('Address')
    previous_supervisor_name_2 = fields.Char('Name')

    personal_reference_name_1 = fields.Char('Name')
    personal_reference_address_1 = fields.Text('Address')
    personal_reference_tel_no_1 = fields.Text('Tel. No.')
    personal_reference_fax_1 = fields.Text('Fax/Email')
    personal_reference_fax_2 = fields.Text('Fax/Email')
    personal_reference_tel_no_2 = fields.Text('Tel. No.')
    personal_reference_address_2 = fields.Text('Address')
    personal_reference_name_2 = fields.Char('Name')

    personal_friends_name_1 = fields.Char('Name')
    personal_friends_address_1 = fields.Text('Address')
    personal_friends_tel_no_1 = fields.Text('Tel. No.')
    personal_friends_fax_1 = fields.Text('Fax/Email')
    personal_friends_fax_2 = fields.Text('Fax/Email')
    personal_friends_tel_no_2 = fields.Text('Tel. No.')
    personal_friends_address_2 = fields.Text('Address')
    personal_friends_name_2 = fields.Char('Name')

    introduced_to_ct = fields.Text('How were you introduced to CT?')
    know_anyone = fields.Text('Do you know anyone (Including relatives) who works at CT?')

    signature = fields.Char('Signature')
    date = fields.Date('Date')
    place = fields.Char('Place')

    # Checklist fields

    candidate_name = fields.Char('Candidate Name')
    candidate_nationality = fields.Many2one(
        'res.country', 'Nationality')

    checklist_ids = fields.One2many('hr.employee.checklist', 'employee_id',
                                    'Checklist',copy=True, default=_default_checklist)

    notes = fields.Text('Notes')
    recruitment_manager_sign = fields.Char('Recruitment Manager Signature')
    recruitment_manager_date = fields.Date('Date')
    admin_manager_sign = fields.Char('Admin Manager Signature')

    admin_manager_date = fields.Date('Date')
    employee_unique_id = fields.Char('Unique ID')
