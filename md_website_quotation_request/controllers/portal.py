# -*- coding: utf-8 -*-
# Powered by Mindphin.
# © 2023 Mindphin. (<https://www.mindphin.com>).

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortalQuotation(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super(CustomerPortalQuotation, self)._prepare_home_portal_values(counters)
        if 'quotation_request_count' in counters:
            # We use sudo() and filter by partner_id to ensure visibility of draft requests
            quotation_request_count = request.env['sale.order'].sudo().search_count([
                ('partner_id', '=', request.env.user.partner_id.id),
                ('quotation_request', '=', True)
            ])
            values['quotation_request_count'] = quotation_request_count
        return values

    @http.route(['/my/requested_quotations', '/my/requested_quotations/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_requested_quotations(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        SaleOrder = request.env['sale.order'].sudo() # Using sudo to ensure all states are visible

        domain = [
            ('partner_id', '=', partner.id),
            ('quotation_request', '=', True)
        ]

        searchbar_sortings = {
            'date': {'label': _('Order Date'), 'order': 'date_order desc'},
            'name': {'label': _('Reference'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'state'},
        }

        # default sortby order
        if not sortby:
            sortby = 'date'
        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = SaleOrder.search_count(domain)
        # make pager
        pager = portal_pager(
            url="/my/requested_quotations",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_quotations_history'] = quotations.ids[:100]

        values.update({
            'date': date_begin,
            'quotations': quotations,
            'page_name': 'requested_quotation',
            'pager': pager,
            'default_url': '/my/requested_quotations',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("md_website_quotation_request.portal_my_requested_quotations", values)
