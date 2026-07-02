from odoo import http
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request


class MyVehiclesPortal(CustomerPortal):

    # =========================
    # Portal Home Counter
    # =========================
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)

        if 'vehicle_count' in counters:
            partner = request.env.user.partner_id
            values['vehicle_count'] = request.env["vehicle.vehicle"].sudo().search_count([
                ("partner_id", "=", partner.id)
            ])

        return values

    # =========================
    # Helpers
    # =========================
    def _get_vehicle_or_redirect(self, vehicle_id):
        partner = request.env.user.partner_id
        vehicle = request.env['vehicle.vehicle'].sudo().browse(vehicle_id)

        if not vehicle.exists() or vehicle.partner_id != partner:
            return None

        return vehicle

    def _to_int(self, val):
        try:
            return int(val)
        except:
            return False

    def _to_float(self, val):
        try:
            return float(val)
        except:
            return 0.0
        


    @http.route(['/my/vehicle/delete/<int:vehicle_id>'], type='http', auth="user", website=True)
    def portal_delete_vehicle(self, vehicle_id, **kw):

        vehicle = self._get_vehicle_or_redirect(vehicle_id)
        if not vehicle:
            return request.redirect('/my/vehicles')

        vehicle.unlink()

        return request.redirect('/my/vehicles')

    # =========================
    # Vehicle List Page
    # =========================
    @http.route(['/my/vehicles', '/my/vehicles/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_vehicles(self, page=1, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        vehicles = request.env["vehicle.vehicle"].sudo().search([
            ("partner_id", "=", partner.id)
        ])

        values.update({
            "vehicles": vehicles,
            "page_name": "vehicles",
        })

        return request.render("my_vehicles_portal.portal_my_vehicles", values)

    # =========================
    # Create Vehicle (GET)
    # =========================
    @http.route(['/my/vehicle/new'], type='http', auth="user", website=True)
    def portal_create_vehicle(self, **kw):
        values = self._prepare_portal_layout_values()

        values.update({
            'page_name': 'vehicles',
            'brands': request.env['vehicle.brand'].sudo().search([]),
            'models': request.env['vehicle.model'].sudo().search([]),
        })

        return request.render('my_vehicles_portal.template_create_vehicle', values)

    # =========================
    # Store Vehicle (POST)
    # =========================
    @http.route(['/my/vehicle/create'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def portal_store_vehicle(self, **post):

        partner = request.env.user.partner_id

        request.env['vehicle.vehicle'].sudo().create({
            'license_plate': post.get('license_plate'),
            'vin': post.get('vin'),
            'year': self._to_int(post.get('year')),

            'fuel_type': post.get('fuel_type'),
            'transmission': post.get('transmission'),
            'doors': str(post.get('doors')),

            'current_mileage': self._to_float(post.get('current_mileage')),

            'brand_id': self._to_int(post.get('brand_id')),
            'model_id': self._to_int(post.get('model_id')),

            # 🔥 AUTO ATTACH USER
            'partner_id': partner.id,
        })

        return request.redirect('/my/vehicles')

    # =========================
    # Edit Vehicle (GET)
    # =========================
    @http.route(['/my/vehicle/edit/<int:vehicle_id>'], type='http', auth="user", website=True)
    def portal_edit_vehicle(self, vehicle_id, **kw):

        vehicle = self._get_vehicle_or_redirect(vehicle_id)
        if not vehicle:
            return request.redirect('/my/vehicles')

        values = self._prepare_portal_layout_values()

        values.update({
            'vehicle': vehicle,
            'page_name': 'vehicles',
            'brands': request.env['vehicle.brand'].sudo().search([]),
            'models': request.env['vehicle.model'].sudo().search([
                ('brand_id', '=', vehicle.brand_id.id)
            ]),
        })

        return request.render('my_vehicles_portal.template_edit_vehicle', values)

    # =========================
    # Update Vehicle (POST)
    # =========================
    @http.route(['/my/vehicle/update/<int:vehicle_id>'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def portal_update_vehicle(self, vehicle_id, **post):

        vehicle = self._get_vehicle_or_redirect(vehicle_id)
        if not vehicle:
            return request.redirect('/my/vehicles')

        vehicle.write({
            'license_plate': post.get('license_plate'),
            'vin': post.get('vin'),
            'year': self._to_int(post.get('year')),

            'fuel_type': post.get('fuel_type'),
            'transmission': post.get('transmission'),
            'doors': str(post.get('doors')),

            'current_mileage': self._to_float(post.get('current_mileage')),

            'brand_id': self._to_int(post.get('brand_id')),
            'model_id': self._to_int(post.get('model_id')),
        })

        return request.redirect('/my/vehicles')

    # =========================
    # AJAX: Get Models by Brand
    # =========================
    @http.route('/get_models_by_brand', type='json', auth='user', csrf=False)
    def get_models_by_brand(self, brand_id):
        models = request.env['vehicle.model'].sudo().search([
            ('brand_id', '=', int(brand_id))
        ])
        return [{'id': m.id, 'name': m.name} for m in models]