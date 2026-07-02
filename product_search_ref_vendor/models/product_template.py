from odoo import models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Surcharge name_search pour inclure les références fournisseur
        """
        if not args:
            args = []
            
        # Recherche standard d'abord
        result = super().name_search(name, args, operator, limit)
        
        # Si pas de résultats et qu'on a un terme de recherche
        if not result and name:
            # Recherche par référence fournisseur
            vendor_products = self.search([
                ('seller_ids.product_code', operator, name)
            ] + args, limit=limit)
            
            if vendor_products:
                result = vendor_products.name_get()
        
        return result