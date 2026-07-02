# -*- coding: utf-8 -*-
{
    "name": "Sale order force invoiced statut",
    "version": "17.0.1.0.0",
    "summary": "Force invoiced status on sale orders",
    "description": """
Sale Force Invoice Status
=========================

This module allows sales managers to manually force the invoice status 
of sales orders to 'invoiced' with proper justification and traceability.

    """,
    "author": "SOSI",
    "category": "Sale",
    "depends": ["sale"],
    "data": [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'views/sale_force_invoice_wizard_views.xml',
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "LGPL-3",
}