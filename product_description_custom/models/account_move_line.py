from odoo import models, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    @api.onchange('product_id')
    def _onchange_product_id_custom_description(self):
        """
        Onchange personnalisé pour les lignes de facture (ventes ET achats)
        """
        if self.product_id and self.move_id and self.move_id.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
            # Récupération du paramètre de configuration
            use_internal_ref = self.env['ir.config_parameter'].sudo().get_param(
                'product_description_custom.use_internal_ref', 'False'
            )
            
            if use_internal_ref != 'True':
                self.name = self._get_account_move_line_description_custom()
    
    def _get_account_move_line_description_custom(self):
        """
        Génère la description de la ligne de facture sans la référence interne
        Fonctionne pour les factures de vente ET d'achat
        """
        self.ensure_one()
        
        if not self.product_id:
            return self.name or ''
        
        # Récupération du nom de base (sans référence interne)
        name = self.product_id.name or ''
        
        # Ajout de la description appropriée selon le type de facture
        if self.move_id.move_type in ['out_invoice', 'out_refund']:
            # Factures de vente : utiliser la description de vente
            if self.product_id.description_sale:
                name += '\n' + self.product_id.description_sale
        elif self.move_id.move_type in ['in_invoice', 'in_refund']:
            # Factures d'achat : utiliser la description d'achat
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            elif self.product_id.description_sale:
                # Fallback sur description de vente si pas de description d'achat
                name += '\n' + self.product_id.description_sale
                
        return name
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Surcharge de la création pour appliquer la logique sur les nouvelles lignes
        """
        lines = super().create(vals_list)
        
        # Récupération du paramètre de configuration
        use_internal_ref = self.env['ir.config_parameter'].sudo().get_param(
            'product_description_custom.use_internal_ref', 'False'
        )
        
        if use_internal_ref != 'True':
            for line in lines:
                if line.product_id and line.move_id.move_type in ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']:
                    line.name = line._get_account_move_line_description_custom()
        
        return lines