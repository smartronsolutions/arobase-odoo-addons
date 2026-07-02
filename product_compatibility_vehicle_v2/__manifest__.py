# -*- coding: utf-8 -*-
{
    "name": "Product Compatibility Categories Vehicle",
    "version": "17.0.1.0.0",
    "summary": "Vehicle compatibility categories for products",
    "description": """
        Module for managing product-vehicle compatibility
        
        Allows you to assign a product to multiple vehicle compatibility categories
        to facilitate filtering and searching.
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