# -*- coding: utf-8 -*-
{
    'name': "Happy & Ruby - Local Purchase",

    'summary': """
        Local Purchase""",

    'description': """
         This module allows HQ user to create an RFQ for local purchases and send it for admin approval.
    """,

    'author': "Loyal IT Solutions PVT LTD",
    'website': "http://www.loyalitsolutions.com",


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Purchase',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'hr_user_group', 'account', 'purchase_stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'views/purchase_order_views.xml',
        'views/templates.xml',
    ],
    'license': 'LGPL-3',
}
