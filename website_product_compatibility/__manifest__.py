# -*- coding: utf-8 -*-
{
    'name': 'Website Product Compatibility',
    'version': '17.0.1.0.8',
    'category': 'Website/eCommerce',
    'summary': 'Vehicle-based product compatibility filter for e-commerce',
    'description': """
Website Product Compatibility Module
=====================================

This module extends Odoo's e-commerce functionality to provide advanced 
vehicle-based product compatibility filtering.

Key Features:
-------------
* **Vehicle Filter**: Search products by vehicle brand, model, year, series, and variant
* **My Vehicle Button**: Quick selection from user's saved vehicles
* **Compatibility Popup**: Modal interface for vehicle selection
* **Auto Search**: Automatic product search after vehicle selection
* **Responsive Design**: Mobile-friendly interface
* **AJAX Loading**: Real-time filtering without page reloads
* **Error Handling**: Graceful error states and loading indicators

User Interface:
---------------
* Vehicle filter card on shop page with cascading dropdowns
* "My Vehicle" button for quick access to saved vehicles
* Modal popup showing user's vehicles in a clean table
* Loading states and empty state messages
* Auto-populated filters after vehicle selection

Technical Features:
-------------------
* Bootstrap 5 compatible
* JSON-RPC API endpoints
* User-specific vehicle filtering
* Comprehensive error logging
* SEO-friendly URL parameters
* Performance optimized with lazy loading

Dependencies:
--------------
* base
* product
* website
* website_sale
* product_compatibility_vehicle_v2

Installation:
--------------
1. Place this module in your Odoo addons directory
2. Update the module list in Odoo
3. Install the module from Apps menu
4. Module will automatically extend the shop page with vehicle filters

Configuration:
---------------
No additional configuration required. The module works out of the box
with the product_compatibility_vehicle_v2 module.

Usage:
------
1. Users navigate to the shop page
2. Use "Search by Vehicle" filter to select their vehicle
3. Or click "My Vehicle" to quickly select from saved vehicles
4. Products compatible with the selected vehicle are displayed

API Endpoints:
--------------
* POST /shop/vehicle/brands - Get all vehicle brands
* POST /shop/vehicle/models - Get models for a brand
* POST /shop/vehicle/years - Get years for a model
* POST /shop/vehicle/series - Get series for a year
* POST /shop/vehicle/variants - Get variants for a series
* POST /shop/user/vehicles - Get user's saved vehicles (auth required)
* POST /shop/vehicle/search - Search for compatible products

Version History:
----------------
* 1.0.6 - Initial release
* 1.0.7 - Added My Vehicle popup
* 1.0.8 - Enhanced error handling and loading states

Author: SOSI
License: LGPL-3
""",
    'author': 'SOSI',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'website',
        'website_sale',
        'product_compatibility_vehicle_v2',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'views/website_template.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_product_compatibility/static/src/css/compatibility_filter.css',
            'website_product_compatibility/static/src/js/compatibility_filter.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
