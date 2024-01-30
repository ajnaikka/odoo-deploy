# -*- coding: utf-8 -*-

{
    'name': 'Technology Force Employee Visa',
    'version': '17.0.0.1',
    'category': 'Human Resources/Employees',
    'sequence': -100,
    'summary': 'Apps for Employee Visa Application',
    'description': """Apps for employee visa application""",
    'author': 'Loyal IT Solution',
    'website': 'https://www.loyalitsolutions.com',
    'depends': ['hr','mail','base','hr_recruitment'],
    'data': [
        'data/visa_mail.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/employee_visa.xml',
        'wizard/mail_compose_wizard.xml'

    ],
    'installable': True,
    'auto_install': False,
}

