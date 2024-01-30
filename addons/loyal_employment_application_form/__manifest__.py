# -*- coding: utf-8 -*-

{
    'name': 'Employment Application',
    'version': '1.3',
    'category': 'Human Resources/Employees',
    'sequence': 95,
    'summary': 'Employment Application Form',
    'website': 'https://www.loyalitsolutions.com',
    'images': [],
    'depends': [
        'hr',
    ],
    'data': [
        "security/ir.model.access.csv",
        'views/hr_employee_view_inherited.xml',
        'views/hr_employee_checklist_form_view.xml'
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
