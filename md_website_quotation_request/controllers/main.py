# -*- coding: utf-8 -*-
# Powered by Mindphin.
# © 2023 Mindphin. (<https://www.mindphin.com>).

from odoo import http
from odoo.http import request


class QuotationMsg(http.Controller):

    @http.route(['/quotation'], type='http', auth="user", website=True)
    def quotation_page(self, **post):
        order = request.website.sale_get_order()
        # Force the quotation request flag
        order.write({'quotation_request': True})
        
        # 1. Force the customer to be a follower (Essential for portal visibility)
        order.sudo().message_subscribe(partner_ids=[order.partner_id.id])
        
        # 2. Force access token generation (Ensures the customer can 'read' the record)
        order.sudo()._portal_ensure_token()
        
        order_reference = order.name
        template = request.env.ref('md_website_quotation_request.email_template_for_quotation')
        template.sudo().send_mail(order.id, force_send=True)
        return request.render("md_website_quotation_request.qt_thanks_page", {
            'order_reference': order_reference,
        })
