# -*- coding: utf-8 -*-

{
    'name': 'Technology Force Employee End of service',
    'version': '17.0.0.1',
    'category': 'Human Resources/Employees',
    'sequence': -100,
    'summary': 'Apps for End of service due to conditions and requirements of business',
    'description': """for End of service due to conditions and requirements of business""",
    'author': 'Loyal IT Solution',
    'website': 'https://www.loyalitsolutions.com',
    'depends': ['hr','mail','base','contacts','tf_approval_user_groups','tf_eos_due_to_contract_termination','tf_end_of_service'],
    'data': [
        'data/termiantaion_business_requirement.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/employee_business_termination.xml',
        'wizard/mail_compose_wizard.xml'
            ],
    'installable': True,
    'auto_install': False,
}

