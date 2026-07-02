from odoo import models, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_name(self):
        """
        Surcharge la méthode de calcul du nom pour personnaliser la description
        """
        # Récupération du paramètre de configuration
        use_internal_ref = self.env['ir.config_parameter'].sudo().get_param(
            'product_description_custom.use_internal_ref', 'False'
        )
        use_internal_ref = use_internal_ref == 'True'
        
        if use_internal_ref:
            # Comportement standard d'Odoo
            return super()._compute_name()
        else:
            # Comportement personnalisé sans référence interne
            for line in self:
                if line.product_id:
                    line.name = line._get_sale_order_line_multiline_description_sale_custom()
                elif not line.name:
                    line.name = ''
    
    def _get_sale_order_line_multiline_description_sale_custom(self):
        """
        Génère la description de la ligne de vente sans la référence interne
        """
        self.ensure_one()
        
        if not self.product_id:
            return self.name or ''
        
        name = self.product_id.name or ''
        
        # Ajout de la description de vente si elle existe
        if self.product_id.description_sale:
            name += '\n' + self.product_id.description_sale
            
        return name
    
    @api.onchange('product_id')
    def _onchange_product_id_custom(self):
        """
        Surcharge du onchange pour appliquer la logique personnalisée
        """
        
        if self.product_id:
            # Récupération du paramètre de configuration
            use_internal_ref = self.env['ir.config_parameter'].sudo().get_param(
                'product_description_custom.use_internal_ref', 'False'
            )
            
            if use_internal_ref != 'True':
                self.name = self._get_sale_order_line_multiline_description_sale_custom()
        