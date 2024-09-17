# -*- coding: utf-8 -*-
{
    'name': "del_payment_approval_cashier",
    'summary': """
        Payment Approval""",
    'description': """
        Payment Approval
    """,
    'author': "del-Ideas Solutions",
    'website': "https://www.delideas.com",
    'category': 'Uncategorized',
    'version': '0.1',
    # any module necessary for this one to work correctly
    'depends': ['base','account','analytic'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
