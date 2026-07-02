# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrder(models.Model):

    _inherit = "sale.order"

    account_payment_ids = fields.One2many('account.payment', 'sale_id',
                                          string="Pay sale advanced",
                                          readonly=True)
    amount_resisual = fields.Float('Residual amount', readonly=True,
                                   store=True, compute="_get_amount_residual", help="Ce Montant affiche uniquement la somme restante du bon de commande en prenant compte des paiements anticipés saisis à travers de ce bon de commande.")

    advance_payment_count = fields.Integer(
        string='Advance Payments Count',
        compute='_compute_advance_payment_count'
    )

    # NOUVEAU: Champ pour vérifier la configuration
    show_residual_config = fields.Boolean(
        string="Show Residual Config",
        compute="_compute_show_residual_config"
    )

    total_advance_payments = fields.Monetary(
        string='Total P. Anticipés',
        compute='_compute_total_advance_payments',
        store=True,
        currency_field='currency_id',
        help="Montant total de tous les paiements anticipés validés pour cette commande"
    )

#    def _get_amount_residual(self):
#        advance_amount = 0.0
#        for line in self.account_payment_ids:
#            if line.state != 'draft':
#                advance_amount += line.amount
#        self.amount_resisual = self.amount_total - advance_amount

    @api.depends()  # Pas de dépendance car on lit un paramètre système
    def _compute_show_residual_config(self):
        """Vérifie si l'option d'affichage du résiduel est activée"""
        show_residual = self.env['ir.config_parameter'].sudo().get_param(
            'sale_advance_payment.show_residual_amount', 'False'
        )
        show = show_residual.lower() in ('true', '1', 'yes', 'on')
        
        for order in self:
            order.show_residual_config = show

    @api.depends('account_payment_ids', 'account_payment_ids.amount', 'account_payment_ids.state', 'amount_total')
    def _get_amount_residual(self):
        for order in self:  # ← CORRECTION: Boucle sur chaque enregistrement
            advance_amount = 0.0
            for payment in order.account_payment_ids:  # ← CORRECTION: order au lieu de self
                if payment.state != 'draft':
                    advance_amount += payment.amount
            order.amount_resisual = order.amount_total - advance_amount  # ← CORRECTION: order au lieu de self

    @api.depends('account_payment_ids')
    def _compute_advance_payment_count(self):
        for order in self:
            order.advance_payment_count = len(order.account_payment_ids.filtered(lambda p: p.state != 'draft'))

    @api.depends('account_payment_ids', 'account_payment_ids.amount', 'account_payment_ids.state')
    def _compute_total_advance_payments(self):
        """Calcule le montant total des paiements anticipés validés"""
        for order in self:
            total = 0.0
            for payment in order.account_payment_ids:
                if payment.state in ('posted', 'sent', 'reconciled'):  # Paiements validés
                    total += payment.amount
            order.total_advance_payments = total