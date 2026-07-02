# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductProduct(models.Model):
    """Extension of product.product for compatibility search"""
    _inherit = 'product.product'

    compatibility_category_ids = fields.Many2many(
        'compatibility.category',
        string=_('Compatibility Categories'),
        related='product_tmpl_id.compatibility_category_ids',
        readonly=True
    )

    compatibility_search_text = fields.Text(
        string=_('Compatibility search text'),
        related='product_tmpl_id.compatibility_search_text',
        store=True,
        index=True
    )

    compatibility_category_count = fields.Integer(
        string=_("Compatibility category count"),
        related='product_tmpl_id.compatibility_category_count',
        store=True
    )

    # ✅ Field for Searchpanel (Many2one only)
    compatibility_category_panel_id = fields.Many2one(
        'compatibility.category',
        string=_("Main Compatibility Category"),
        compute="_compute_compatibility_category_panel",
        store=True,
        index=True
    )

    # ✅ Related fields for search & filters
    complete_name = fields.Char(
        related="compatibility_category_panel_id.complete_name",
        store=True,
        index=True
    )
    brand_id = fields.Many2one(
        related="compatibility_category_panel_id.brand_id",
        store=True,
        index=True
    )
    model_id = fields.Many2one(
        related="compatibility_category_panel_id.model_id",
        store=True,
        index=True
    )
    year_id = fields.Many2one(
        related="compatibility_category_panel_id.year_id",
        store=True,
        index=True
    )
    series_id = fields.Many2one(
        related="compatibility_category_panel_id.series_id",
        store=True,
        index=True
    )
    variant_id = fields.Many2one(
        related="compatibility_category_panel_id.variant_id",
        store=True,
        index=True
    )

    @api.depends('compatibility_category_ids')
    def _compute_compatibility_category_panel(self):
        """Assign the first compatibility category for searchpanel"""
        for product in self:
            product.compatibility_category_panel_id = (
                product.compatibility_category_ids[:1].id
                if product.compatibility_category_ids
                else False
            )
