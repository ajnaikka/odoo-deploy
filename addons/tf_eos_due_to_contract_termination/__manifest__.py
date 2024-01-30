# -*- coding: utf-8 -*-

{
    'name': 'Technology Force Employee Termination',
    'version': '17.0.0.1',
    'category': 'Human Resources/Employees',
    'sequence': -100,
    'summary': 'Apps for Employee Termination',
    'description': """Apps for employee termination form""",
    'author': 'Loyal IT Solution',
    'website': 'https://www.loyalitsolutions.com',
    'depends': ['hr','mail','base','contacts','tf_approval_user_groups','tf_end_of_service'],
    'data': [
        'data/termination_form_group.xml',
        'data/termination_mail.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/employee_termination.xml',
        'wizard/mail_compose_wizard.xml'

    ],
    'installable': True,
    'auto_install': False,
}

