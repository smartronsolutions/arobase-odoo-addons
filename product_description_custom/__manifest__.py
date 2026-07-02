{
    'name': 'Product Description Custom',
    'version': '17.0.1.0.0',
    'category': 'Sales/Purchase',
    'summary': 'Personnalise la description des produits dans les devis et factures',
    'description': """
    Ce module permet de personnaliser l'affichage de la description des produits
    dans les lignes de devis et factures en excluant la référence interne.
    
    Fonctionnalités :
    - Supprime la référence interne de la description automatique
    - Option configurable pour réactiver l'ancien comportement
    - Affecte les devis, commandes, factures de vente ET factures d'achat
    """,
    'author': 'SOSI',
    'depends': ['sale', 'account', 'product'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}