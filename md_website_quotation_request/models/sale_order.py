# -*- coding: utf-8 -*-
# Powered by Mindphin.
# Fixed & optimized version

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    quotation_request = fields.Boolean(string="Quotation Request")

    # ------------------------------
    # Email Template Logic
    # ------------------------------
    def _find_mail_template(self):
        self.ensure_one()
        if self.state == 'draft' and self.quotation_request:
            return self.env.ref('sale.email_template_edi_sale', raise_if_not_found=False)
        return self._get_confirmation_template()

    # ------------------------------
    # Portal Access URL
    # ------------------------------
    def _compute_access_url(self):
        super()._compute_access_url()
        for order in self:
            if order.quotation_request:
                order.access_url = f'/my/orders/{order.id}'

    # ------------------------------
    # Create Override
    # ------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)

        for order in orders:
            if order.quotation_request:
                # Ensure customer is follower
                if order.partner_id:
                    order.message_subscribe(partner_ids=[order.partner_id.id])

                # Ensure portal token exists
                if not order.access_token:
                    order._portal_ensure_token()

        return orders

    # ------------------------------
    # Portal Domain Fix (SAFE WAY)
    # ------------------------------
    def _get_portal_domain(self):
        domain = super()._get_portal_domain()

        if self.env.user.has_group('base.group_portal'):
            partner_id = self.env.user.partner_id.id

            # Allow:
            # - normal orders
            # - OR quotation requests in draft
            domain = ['|'] + domain + [
                '&',
                ('quotation_request', '=', True),
                ('partner_id', '=', partner_id)
            ]

        return domain