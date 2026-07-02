# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class VehicleProductSearch(models.TransientModel):
    """Search products by vehicle (new hierarchy)"""
    _name = 'vehicle.product.search'
    _description = 'Search products by vehicle'

    name = fields.Char(string=_("Vehicle Name"))

    @api.onchange('name')
    def _onchange_name(self):
        """Update selected_vehicle_path whenever name changes"""
        for record in self:
            record.selected_vehicle_path = record.name or ''

    # Vehicle hierarchy (pluralized models)
    brand_id = fields.Many2one('vehicle.brands', string=_('Brand'))
    model_id = fields.Many2one(
        'vehicle.models',
        string=_('Model'),
        domain="[('brand_id','=',brand_id)]"
    )
    year_id = fields.Many2one(
        'vehicle.years',
        string=_('Year'),
        domain="[('model_id','=',model_id)]"
    )
    series_id = fields.Many2one(
        'vehicle.serieses',
        string=_('Series'),
        domain="[('year_id','=',year_id)]"
    )
    variant_id = fields.Many2one(
        'vehicle.variants',
        string=_('Variant'),
        domain="[('series_id','=',series_id)]"
    )

    product_category_id = fields.Many2one('product.category', string=_('Product category'))

    product_count = fields.Integer(string=_('Product count'), compute='_compute_search_results')
    product_ids = fields.Many2many(
        'product.template',
        string=_('Compatible products'),
        compute='_compute_search_results'
    )

    search_info = fields.Text(string=_('Search information'), compute='_compute_search_info')
    selected_vehicle_path = fields.Char(string=_('Selected vehicle path'), compute='_compute_selected_vehicle_path')

    # ---------------- COMPUTE ----------------
    @api.depends('brand_id', 'model_id', 'year_id', 'series_id', 'variant_id', 'product_category_id')
    def _compute_search_results(self):
        """Compute product_ids and product_count based on selected vehicle hierarchy."""
        Compatibility = self.env['compatibility.category']
        for rec in self:
            rec.product_ids = [(5, 0, 0)]
            rec.product_count = 0

            # Determine most precise vehicle level selected
            for level in ['variant', 'series', 'year', 'model', 'brand']:
                level_id = getattr(rec, f"{level}_id")
                if level_id:
                    compat_dom = [(f"{level}_id", '=', level_id.id)]
                    break
            else:
                continue  # nothing selected

            compat_cats = Compatibility.search(compat_dom)
            if not compat_cats:
                continue

            # Retrieve products from compatibility categories
            products = self.env['product.template'].browse()
            for field in ['product_ids', 'product_template_ids', 'product_id']:
                if hasattr(compat_cats, field):
                    products = compat_cats.mapped(field)
                    if field == 'product_id':
                        products = products.mapped('product_tmpl_id')
                    break

            # Optional filter by product category
            if products and rec.product_category_id:
                products = products.filtered(lambda p: p.categ_id == rec.product_category_id)

            rec.product_ids = [(6, 0, products.ids)]
            rec.product_count = len(products)

    # ---------------- INFO & PATH ----------------
    @api.depends('brand_id', 'model_id', 'year_id', 'series_id', 'variant_id', 'product_count')
    def _compute_search_info(self):
        for rec in self:
            parts = []
            if rec.brand_id:
                parts.append(_("Brand: %s") % rec.brand_id.name)
            if rec.model_id:
                parts.append(_("Model: %s") % rec.model_id.name)
            if rec.year_id:
                parts.append(_("Year: %s") % rec.year_id.name)
            if rec.series_id:
                parts.append(_("Series: %s") % rec.series_id.name)
            if rec.variant_id:
                parts.append(_("Variant: %s") % rec.variant_id.name)
            if rec.product_category_id:
                parts.append(_("Category: %s") % rec.product_category_id.name)

            if parts:
                rec.search_info = "%s\n\n%s: %d" % (" → ".join(parts), _("Result"), rec.product_count)
            else:
                rec.search_info = _("No criteria selected")

    @api.depends('brand_id', 'model_id', 'year_id', 'series_id', 'variant_id')
    def _compute_selected_vehicle_path(self):
        for rec in self:
            parts = [x.name for x in [rec.brand_id, rec.model_id, rec.year_id, rec.series_id, rec.variant_id] if x]
            path = " / ".join(parts) if parts else ""
            rec.selected_vehicle_path = path
            rec.name = path

    # ---------------- ONCHANGE ----------------
    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        self.model_id = False
        self.year_id = False
        self.series_id = False
        self.variant_id = False

    @api.onchange('model_id')
    def _onchange_model_id(self):
        self.year_id = False
        self.series_id = False
        self.variant_id = False

    @api.onchange('year_id')
    def _onchange_year_id(self):
        self.series_id = False
        self.variant_id = False

    @api.onchange('series_id')
    def _onchange_series_id(self):
        self.variant_id = False

    # ---------------- ACTIONS ----------------
    def action_view_products(self):
        self.ensure_one()
        if not self.product_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('No products'),
                    'message': _('No compatible products found with these criteria.'),
                    'type': 'warning',
                }
            }
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compatible Products'),
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.product_ids.ids)],
            'target': 'current',
        }

    def action_reset_search(self):
        self.brand_id = False
        self.model_id = False
        self.year_id = False
        self.series_id = False
        self.variant_id = False
        self.product_category_id = False
        self.product_ids = [(5, 0, 0)]
        self.product_count = 0
        return {
            'type': 'ir.actions.act_window',
            'name': _('🔍 Search by vehicle'),
            'res_model': 'vehicle.product.search',
            'view_mode': 'form',
            'target': 'current',
            'context': {},
        }
