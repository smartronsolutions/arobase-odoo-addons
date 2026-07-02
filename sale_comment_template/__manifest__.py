{
    "name": "Sale Comments",
    "summary": "Comments templates on sale order documents",
    "version": "17.0.1.0.0",
    "category": "Sale",
    "author": "SOSI",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "sale",
        "base_comment_template",
    ],
    "data": [
        "views/sale_order_view.xml",
        "views/report_saleorder.xml",
        "security/ir.model.access.csv",
        "views/base_comment_template_view.xml",
    ],
}
