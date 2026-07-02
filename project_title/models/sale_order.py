# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    project_title = fields.Char(string=_("Titre"), help=_("Titre de vos travaux"))
    
    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        res['project_title'] = self.project_title
        return res