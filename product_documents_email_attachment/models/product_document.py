# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProductDocument(models.Model):
    _inherit = 'product.document'

    include_in_email = fields.Boolean(
        string=_("Attach to email"),
        default=False,
        help=_("If checked, this document will be automatically attached when sending quotes by email containing this product.")
    )