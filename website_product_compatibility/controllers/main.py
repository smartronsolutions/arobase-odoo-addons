# -*- coding: utf-8 -*-

import json
import logging

from odoo import http
from odoo.http import request
from odoo.osv import expression
from odoo.addons.website_sale.controllers.main import WebsiteSale

_logger = logging.getLogger(__name__)


# ==========================================
# SAFE JSON PARSER
# ==========================================
def _vehicle_post_params():
    """
    Safely extract JSON-RPC parameters from request body.
    Handles both standard JSON and JSON-RPC 2.0 format.
    """
    if not request.httprequest.data:
        return {}

    try:
        data = json.loads(request.httprequest.data.decode('utf-8'))
    except Exception as e:
        _logger.warning('Failed to parse JSON request: %s', str(e))
        return {}

    if not isinstance(data, dict):
        return {}

    # Handle JSON-RPC 2.0 format
    if data.get('jsonrpc') == '2.0':
        return data.get('params') or {}

    return data


# ==========================================
# MAIN CONTROLLER
# ==========================================
class VehicleWebsiteSale(WebsiteSale):
    """
    Extended WebsiteSale controller to handle vehicle-based product filtering
    and compatibility searches.
    """

    # ==========================================
    # SHOP FILTER HOOK
    # ==========================================
    def _shop_lookup_products(self, attrib_set, options, post, search, website):
        """
        Override product lookup to support vehicle-based filtering.
        When 'products' parameter is passed in URL, filter to those specific products.
        """
        raw = request.httprequest.args.get('products')

        if raw:
            try:
                id_list = [int(x) for x in raw.split(',') if x.strip().isdigit()]

                if id_list:
                    Product = request.env['product.template'].with_context(bin_size=True)

                    domain = expression.AND([
                        [('id', 'in', id_list)],
                        request.website.sale_product_domain(),
                    ])

                    products = Product.search(domain)

                    # Preserve the order from the URL parameter
                    order_map = {pid: idx for idx, pid in enumerate(id_list)}
                    products = products.sorted(
                        key=lambda p: order_map.get(p.id, 999)
                    )

                    return search or '', len(products), products
            except Exception as e:
                _logger.warning('Error processing products parameter: %s', str(e))

        return super()._shop_lookup_products(
            attrib_set, options, post, search, website
        )

    # ==========================================
    # 🔥 MY VEHICLES (POPUP DATA)
    # ==========================================
    @http.route('/shop/user/vehicles', type='http', auth='user', methods=['POST'], csrf=False)
    def get_user_vehicles(self):
        """
        Retrieve all vehicles associated with the current user.
        Returns a list of vehicles with brand and model information.
        """
        try:
            partner = request.env.user.partner_id

            if not partner:
                return request.make_json_response([])

            vehicles = request.env['vehicle.vehicle'].sudo().search([
                ('partner_id', '=', partner.id)
            ])

            vehicle_data = []
            for v in vehicles:
                try:
                    # Original fields
                    data = {
                        'id': v.id,
                        'brand_id': v.brand_id.id if v.brand_id else False,
                        'brand_name': v.brand_id.name if v.brand_id else 'Unknown',
                        'model_id': v.model_id.id if v.model_id else False,
                        'model_name': v.model_id.name if v.model_id else 'Unknown',
                        'display_name': '{} {}'.format(
                            v.brand_id.name if v.brand_id else '',
                            v.model_id.name if v.model_id else ''
                        ).strip(),
                    }
                    
                    # Enhanced fields (added on top)
                    data.update({
                        'year_id': v.year_id.id if hasattr(v, 'year_id') and v.year_id else False,
                        'series_id': v.series_id.id if hasattr(v, 'series_id') and v.series_id else False,
                        'variant_id': v.variant_id.id if hasattr(v, 'variant_id') and v.variant_id else False,
                        'comp_brand_id': False,
                        'comp_model_id': False,
                        'comp_year_id': False,
                        'comp_series_id': False,
                        'comp_variant_id': False,
                    })
                    
                    # Compatibility logic
                    if hasattr(v, 'compatibility_category_ids') and v.compatibility_category_ids:
                        comp = v.compatibility_category_ids[0]
                        data.update({
                            'comp_brand_id': comp.brand_id.id if comp.brand_id else False,
                            'comp_model_id': comp.model_id.id if comp.model_id else False,
                            'comp_year_id': comp.year_id.id if comp.year_id else False,
                            'comp_series_id': comp.series_id.id if comp.series_id else False,
                            'comp_variant_id': comp.variant_id.id if comp.variant_id else False,
                        })
                    
                    vehicle_data.append(data)
                except Exception as e:
                    _logger.warning('Error processing vehicle %s: %s', v.id, str(e))
                    continue

            return request.make_json_response(vehicle_data)

        except Exception as e:
            _logger.error('Error in get_user_vehicles: %s', str(e))
            return request.make_json_response([])

    # ==========================================
    # BRANDS
    # ==========================================
    @http.route('/shop/vehicle/brands', type='http', auth='public', methods=['POST'], csrf=False)
    def get_brands(self):
        """
        Retrieve all available vehicle brands.
        """
        try:
            brands = request.env['vehicle.brands'].sudo().search([], order='name ASC')

            return request.make_json_response([
                {'id': b.id, 'name': b.name}
                for b in brands
            ])

        except Exception as e:
            _logger.error('Error in get_brands: %s', str(e))
            return request.make_json_response([])

    # ==========================================
    # MODELS
    # ==========================================
    @http.route('/shop/vehicle/models', type='http', auth='public', methods=['POST'], csrf=False)
    def get_models(self):
        """
        Retrieve vehicle models for a specific brand.
        """
        try:
            kw = _vehicle_post_params()
            brand_id = kw.get('brand_id')

            if not brand_id:
                return request.make_json_response([])

            models = request.env['vehicle.models'].sudo().search([
                ('brand_id', '=', int(brand_id))
            ], order='name ASC')

            return request.make_json_response([
                {'id': m.id, 'name': m.name}
                for m in models
            ])

        except Exception as e:
            _logger.error('Error in get_models: %s', str(e))
            return request.make_json_response([])

    # ==========================================
    # YEARS
    # ==========================================
    @http.route('/shop/vehicle/years', type='http', auth='public', methods=['POST'], csrf=False)
    def get_years(self):
        """
        Retrieve production years for a specific vehicle model.
        """
        try:
            kw = _vehicle_post_params()
            model_id = kw.get('model_id')

            if not model_id:
                return request.make_json_response([])

            years = request.env['vehicle.years'].sudo().search([
                ('model_id', '=', int(model_id))
            ], order='name ASC')

            return request.make_json_response([
                {'id': y.id, 'name': y.name}
                for y in years
            ])

        except Exception as e:
            _logger.error('Error in get_years: %s', str(e))
            return request.make_json_response([])

    # ==========================================
    # SERIES
    # ==========================================
    @http.route('/shop/vehicle/series', type='http', auth='public', methods=['POST'], csrf=False)
    def get_series(self):
        """
        Retrieve vehicle series for a specific year.
        """
        try:
            kw = _vehicle_post_params()
            year_id = kw.get('year_id')

            if not year_id:
                return request.make_json_response([])

            series = request.env['vehicle.serieses'].sudo().search([
                ('year_id', '=', int(year_id))
            ], order='name ASC')

            return request.make_json_response([
                {'id': s.id, 'name': s.name}
                for s in series
            ])

        except Exception as e:
            _logger.error('Error in get_series: %s', str(e))
            return request.make_json_response([])

    # ==========================================
    # VARIANTS
    # ==========================================
    @http.route('/shop/vehicle/variants', type='http', auth='public', methods=['POST'], csrf=False)
    def get_variants(self):
        """
        Retrieve vehicle variants for a specific series.
        """
        try:
            kw = _vehicle_post_params()
            series_id = kw.get('series_id')

            if not series_id:
                return request.make_json_response([])

            variants = request.env['vehicle.variants'].sudo().search([
                ('series_id', '=', int(series_id))
            ], order='name ASC')

            return request.make_json_response([
                {'id': v.id, 'name': v.name}
                for v in variants
            ])

        except Exception as e:
            _logger.error('Error in get_variants: %s', str(e))
            return request.make_json_response([])

    # ==========================================
    # COMPATIBILITY SEARCH
    # ==========================================
    @http.route('/shop/vehicle/search', type='http', auth='public', methods=['POST'], csrf=False)
    def vehicle_search(self):
        """
        Search for products compatible with the selected vehicle configuration.
        Creates a search record and returns matching product IDs.
        """
        try:
            kw = _vehicle_post_params()

            # Validate required brand_id
            if not kw.get('brand_id'):
                return request.make_json_response({
                    'products': [],
                    'count': 0,
                    'path': '',
                    'error': 'Brand is required'
                })

            # Create search record
            search = request.env['vehicle.product.search'].sudo().create({
                'brand_id': int(kw['brand_id']) if kw.get('brand_id') else False,
                'model_id': int(kw['model_id']) if kw.get('model_id') else False,
                'year_id': int(kw['year_id']) if kw.get('year_id') else False,
                'series_id': int(kw['series_id']) if kw.get('series_id') else False,
                'variant_id': int(kw['variant_id']) if kw.get('variant_id') else False,
            })

            return request.make_json_response({
                'products': search.product_ids.ids if search.product_ids else [],
                'count': search.product_count if hasattr(search, 'product_count') else len(search.product_ids),
                'path': search.selected_vehicle_path if hasattr(search, 'selected_vehicle_path') else '',
            })

        except Exception as e:
            _logger.error('Error in vehicle_search: %s', str(e))
            return request.make_json_response({
                'products': [],
                'count': 0,
                'path': '',
                'error': str(e)
            })
