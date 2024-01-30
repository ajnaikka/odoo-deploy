# -*- coding: utf-8 -*-

{
    'name': 'Technology Employee Referral',
    'version': '17.0.0.1',
    'category': 'Human Resources/Employees',
    'sequence': -100,
    'summary': 'Apps for Referring an employee',
    'description': """for Referring an employee""",
    'author': 'Loyal IT Solution',
    'website': 'https://www.loyalitsolutions.com',
    'depends': ['hr','mail','base','contacts','base_setup','hr_recruitment','tf_approval_user_groups'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/mail_template.xml',
        'data/sequence.xml',
        'views/employee_referral.xml',
        'views/hr_applicant.xml',
        'wizard/mail_compose_wizard.xml'
            ],
    'installable': True,
    'auto_install': False,
}

