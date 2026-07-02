# -*- coding: utf-8 -*-
# Powered by Mindphin.
# © 2023 Mindphin. (<https://www.mindphin.com>).
{
    'name': 'Website Quotation Request',
    'author': 'Mindphin',
    'license': 'OPL-1',
    'website': "https://www.mindphin.com",
    'support': 'info@mindphin.com',
    'version': '17.0.1.2',
    'category': 'Website',
    'summary': """Odoo allows users to request a precise price quote from Odoo before they proceed to checkout by using the "Website Quotation Request" module. Our administrators adjust the backend and send a quotation to users along with a payment link in order to ensure they have a clear picture of the cost before making a purchase, resulting in a more transparent and convenient buying process.
    Website Quotation Request | Quote Request | website orders | Request quotation | Website Quotation | Website request |  Website orders | Customer request
    """,
    'description': """The Website Quotation Request is a designed to enhance the shopping experience on our website by offering customers a seamless and transparent process for obtaining pricing information, making adjustments, and facilitating secure transactions.
    """,
    'depends': ['website_sale', 'sale_management', 'portal'],
    'data': [
        'security/ir_rule.xml',
        'data/mail_template_data.xml',
        'views/view.xml',
        'views/website_template.xml',
        'views/portal_template.xml',
    ],
    'images': [
        'static/description/banner.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 35,
    'currency': 'USD',
}
