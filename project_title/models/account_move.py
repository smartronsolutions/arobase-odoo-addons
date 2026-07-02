# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMove(models.Model):
    _inherit = "account.move"

    project_title = fields.Char(string=_("Titre"), help=_("Titre de vos travaux"))