from odoo import models, fields, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    use_product_internal_ref_in_description = fields.Boolean(
        string=_("Inclure la référence interne dans la description"),
        config_parameter='product_description_custom.use_internal_ref',
        default=False,
        help=_("Si coché, la référence interne du produit sera incluse dans la description des lignes de devis et factures")
    )