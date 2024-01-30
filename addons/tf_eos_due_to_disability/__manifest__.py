# -*- coding: utf-8 -*-

{
    'name': 'Technology Force Employee End of service',
    'version': '17.0.0.1',
    'category': 'Human Resources/Employees',
    'sequence': -100,
    'summary': 'Apps for End of service due to Non-Fitness and Total Disability',
    'description': """for End of service due to Non-Fitness and Total Disability""",
    'author': 'Loyal IT Solution',
    'website': 'https://www.loyalitsolutions.com',
    'depends': ['hr','mail','base','contacts','tf_approval_user_groups','tf_end_of_service'],
    'data': [
        'data/termiantaion_due_to_disability_mail.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/employee_termination_due_to_disability.xml',
        'wizard/mail_compose_wizard.xml'
            ],
    'installable': True,
    'auto_install': False,
}

