# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    partner_phone = fields.Char(
        string='Téléphone',
        related='partner_id.phone',
        readonly=True,
        store=True,
        help='Numéro de téléphone du partenaire'
    )
    
    partner_mobile = fields.Char(
        string='Mobile',
        related='partner_id.mobile',
        readonly=True,
        store=True,
        help='Numéro de mobile du partenaire'
    )