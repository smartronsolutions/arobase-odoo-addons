from odoo import models

class PosSession(models.Model):
    _inherit = "pos.session"

    def _loader_params_res_users(self):
        result = super()._loader_params_res_users()
        result['search_params']['fields'].append('limited_discount')
        return result