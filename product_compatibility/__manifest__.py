# -*- coding: utf-8 -*-
{
    "name": "Product Compatibility Categories",
    "version": "17.0.1.0.0",
    "summary": "Catégories de compatibilité pour produits",
    "description": """
        Module pour gérer les compatibilités produits via un système 
        de catégories hiérarchiques parallèle aux catégories produit natives.
        
        Permet d'affecter un produit à plusieurs catégories de compatibilité
        pour faciliter le filtrage et la recherche.
    """,
    "author": "SOSI",
    "category": "Inventory",
    "depends": ["base", "product", "stock", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/compatibility_category_view.xml",
        "views/product_template_view.xml",
        "views/search_catalog_views.xml",
        "views/product_compatibility_view_views.xml",
        "views/menu_views.xml",
        "views/compatibility_category_2nd.xml",
        "views/vehicle_product_search_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
}