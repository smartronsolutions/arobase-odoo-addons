{
    'name': 'Phone and mobile in Invoice and Quote',
    'version': '17.0.1.0.0',
    'category': 'Sales',
    'summary': 'Affiche les numéros de téléphone et mobile dans les formulaires devis et factures',
    'author': 'Marie NGUYEN',
    'depends': ['sale', 'account'],
    'data': [
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}