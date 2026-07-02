# -*- coding: utf-8 -*-

{
    'name': 'Account Invoice Digitization',
    'summary': 'Digitize your vendor bills and invoices with OCR and Artificial Intelligence | Invoice automation | ChatGPT | GPT | Automate Accounting',
    'description': "Digitize your vendor bills and invoices with OCR and Artificial Intelligence",
    'category': 'Accounting/Accounting',
    'author': 'Omicron Odoo',
    'version': '17.0.2.1',
    'depends': [
        'account', 'mail'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 279.00,
    'assets': {
        'web.assets_backend': [
            'account_invoice_digitization/static/src/attachment_viewer/attachment_model.js',
            'account_invoice_digitization/static/src/attachment_viewer/attachment_list.js',
            'account_invoice_digitization/static/src/attachment_viewer/attachment_viewer.xml',
        ]
    },
    'external_dependencies': {
        'python': ['pytesseract', 'pypdf', 'pdf2image']
    },
    'images': ['static/description/main_screenshot.png'],
    'live_test_url': 'https://odooapps-demo.winotto.com'
}
