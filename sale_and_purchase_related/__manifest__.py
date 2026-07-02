{
    'name': 'Sale Purchase Order Link',
    'version': '17.0.1.0.0',
    'category': 'Sales/Purchase',
    'summary': 'Link Sale Orders with Purchase Orders and add supplier status tracking',
    'description': """
Sale Purchase Order Link
========================

This module creates bidirectional links between Sale Orders and Purchase Orders:

Features:
---------
* Automatic linking during replenishment process
* New supplier status on Sale Orders (pending/validated)
* Bidirectional Many2many relationship
* Smart buttons with counters
* Automatic status computation based on linked Purchase Orders

Technical:
----------
* Extends sale.order and purchase.order models
* Adds sale_purchase_rel relationship table
* Computes supplier status automatically
* Updates linked orders when status changes
    """,
    'author': 'SOSI',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'purchase',
        'stock',
        'sale_stock',
        'purchase_stock',
    ],
    'data': [
        'views/sale_order_views.xml',
        'views/purchase_order_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}