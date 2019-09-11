# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Products & Pricelists Extend add code',
    'version': '11.0.0.1.0',
    'category': 'Sales',
    'depends': ['product', 'sale', 'stock', 'sale_product_set'],
    'author': 'Rosen Vladimirov, dXFactor Ltd, Aneli Kolicheva',
    'description': """
Add code to price rules.
    """,
    'data': [
        'views/product_pricelist_views.xml',
        'views/sale_views.xml',
        'views/product_set.xml',
        'views/product_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
