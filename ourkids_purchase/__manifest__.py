# -*- coding: utf-8 -*-
{
    'name': "OurKids Purchase",

    'summary': """
        OurKids Purchase """,


    'author': "ITSS , Mahmoud Naguib",
    'website': "http://www.itss-c.com",

    'category': 'purchase',
    'version': '1.3',

    # any module necessary for this one to work correctly
    'depends': ['purchase','purchase_discount_rule'],

    # always loaded
    'data': [
        'views/purchase_order_line.xml',
        'views/purchase_order.xml',
    ],



}