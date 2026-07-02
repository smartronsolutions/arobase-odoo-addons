# -*- coding: utf-8 -*-

{
    "name": "Sale Advance Payment",
    "version": "1.0.0",
    "author": "SOSI",
    "category": "Sales",
    "description": """Allow to add advance payments on sales and then use its
 on invoices""",
    "depends": ["base", "sale", "account"],
    "data": ["wizard/sale_advance_payment_wzd_view.xml",
             "views/sale_view.xml",
             "views/report_sale_order.xml",
             "views/res_config_setting_view.xml",
             "security/ir.model.access.csv"],
    "installable": True,
}
