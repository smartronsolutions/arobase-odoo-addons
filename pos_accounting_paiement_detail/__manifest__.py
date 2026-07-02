{
    'name': 'POS Payment Detail Accounting Entries',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Genere les ecritures comptable individuel de chaque paiement des PdV',
    'description': """
        Ce module modifie le comportement standard d'Odoo pour générer
        une écriture comptable individuelle pour chaque paiement POS
        au lieu de les consolider par méthode de paiement.
    """,
    'author': 'Marie NGUYEN',
    'depends': ['point_of_sale', 'account'],
    'data': [
        'views/pos_config_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}