# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Option pour afficher le montant résiduel
    show_residual_amount = fields.Boolean(
        string="Afficher le montant residuel",
        config_parameter='sale_advance_payment.show_residual_amount',
        help="Si coché, affiche en interne le montant résiduel du devis en prenant compte des paiements anticipés"
    )

    # Option pour afficher les paiements anticipés dans les rapports
    show_advance_payments_in_reports = fields.Boolean(
        string="Afficher les paiements anticipes dans les rapports",
        config_parameter='sale_advance_payment.show_advance_payments_in_reports',
        help="Si coché, affiche la liste des paiements anticipés dans les rapports des commandes clients"
    )
