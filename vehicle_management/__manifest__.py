{
    'name': 'Vehicle Management',
    'version': '17.0.1.0.0',
    'category': 'Sales/CRM',
    'summary': 'Customer vehicle management',
    'description': """
        Customer vehicle management module
        - Brand and model management
        - Vehicle tracking by customer
        - Mileage tracking
        - Billing integration
    """,
    'author': 'SOSI',
    'depends': ['base', 'sale', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_brand_views.xml',
        'views/vehicle_model_views.xml',
        'views/vehicle_vehicle_views.xml',
        'views/res_partner_views.xml',
        'views/vehicle_mileage_views.xml',
#        'views/vehicle_invoice_wizard_views.xml',
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/vehicle_menu.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}