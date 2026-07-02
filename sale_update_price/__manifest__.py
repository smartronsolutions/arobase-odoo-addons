{
    'name': 'Sale Order Fiscal Position Price Update',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Displays the price update link when changing tax status',
    'description': """
        Simple module that automatically activates the display of the 
        “Update prices” link when the tax position is changed
         in a sales order.
        
    """,
    'author': 'SOSI',
    'depends': ['sale'],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}