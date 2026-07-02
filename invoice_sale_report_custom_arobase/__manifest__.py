    {
        'name': 'Custom Invoice & Quote Reports AROBASE',
        'version': '17.0.1.0.0',
        'category': 'Accounting',
        'summary': 'Add internal reference and stock availability to invoice and quote reports',
        'depends': ['account', 'sale', 'stock'],
        'data': [
            'reports/invoice_report.xml',
            'reports/sale_order_report.xml',
            'reports/purchase_order_report.xml',
        ],
        'installable': True,
        'application': False,
    }