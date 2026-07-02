from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    need_price_update = fields.Boolean(
        string=_("Need Price Update After Fiscal Position Change"),
        store=True,
        default=False
    )

    def action_update_taxes(self):
        """
        Override de la méthode update_taxes pour afficher automatiquement
        le lien de mise à jour des prix après la mise à jour des taxes
        """
        # Appel de la méthode parent (mise à jour des taxes)
        result = super().action_update_taxes()
        
        # Affiche le lien de mise à jour des prix après la mise à jour des taxes
        self.need_price_update = True
            
        return result

    def action_update_prices(self):
        """
        Override pour remettre le flag à False après mise à jour des prix
        """
        # Appel de la méthode parent (mise à jour des prix)
        result = super().action_update_prices()
        
        # Remet le flag à False après la mise à jour
        self.need_price_update = False
        
        return result