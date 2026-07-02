# -*- coding: utf-8 -*-

{
    "name": "Project Title",
    "version": "17.0.1.0.0",
    "author": "SOSI",
    "category": "Sales",
    "description": """Permet de mettre un titre à vos devis
 et factures""",
    "depends": ["base", "sale", "account"],
    "data": ["views/account_move_view.xml",
             "views/sale_order_view.xml",
             "reports/sale_account_report.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
