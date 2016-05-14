# -*- coding: utf-8 -*-
{
    'name': "众包物流",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
       众包物流
    """,

    'author': "LI",
    'website': "http://www.lehmaninter.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web', 'decimal_precision'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/logistics_confirm_check.xml',

         'views/templates.xml',
         'views/partner_view.xml',
         'views/views.xml',
        'data/logistic_data.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'auto_install':False,
}