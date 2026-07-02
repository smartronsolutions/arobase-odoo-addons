# -*- coding: utf-8 -*-
{
    'name': 'Product Documents Email Attachment',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Attach product documents to quote emails automatically',
    'description': """
        This module extends the product document functionality to allow
        automatic attachment of product documents when sending quotes by email.
        
        Features:
        - Add checkbox to product documents for email inclusion
        - Automatically attach selected documents when sending quotes
        - Avoid duplicates when same product appears multiple times
    """,
    'author': 'SOSI',
    'depends': [
        'sale',
        'product',
        'mail',
#        'base',
    ],
    'data': [
        'views/product_document_views.xml',
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}