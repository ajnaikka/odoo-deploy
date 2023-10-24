# -*- coding: utf-8 -*-
{
    'name': "Happy & Ruby - Branch Transfer",

    'summary': """
        This module allows the branch user to create a branch transfer request to another branch.""",

    'description': """
        This module allows the branch user to create a branch transfer request to another branch.
    """,

    'author': "Loyal IT Solutions PVT LTD",
    'website': "http://www.loyalitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory/Inventory',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'hr_user_group', 'branch'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/branch_transfer_request_views.xml',
        'views/stock_picking_view.xml',
        'views/stock_location_view.xml',
        'views/product_view.xml',
        'views/templates.xml',
    ],
    'license': 'LGPL-3',
}
