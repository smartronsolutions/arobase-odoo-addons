from odoo import models, fields, api, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    has_replenishment = fields.Boolean(
        string=_('Has Replenishment'),
        compute='_compute_has_replenishment',
        help=_('Indicates if this product has replenishment configuration')
    )
    
    replenishment_icon = fields.Html(
        compute='_compute_has_replenishment'
    )
    
    @api.depends('product_id', 'product_id.route_ids', 'product_id.seller_ids')
    def _compute_has_replenishment(self):
        """Vérifie si le produit a une configuration de réapprovisionnement"""
        for line in self:
            if not line.product_id or line.product_id.type != 'product':
                line.has_replenishment = False
                line.replenishment_icon = ''
                continue
            
            # Vérifier si le produit a la route "Buy" (réapprovisionnement par achat)
            buy_route = self.env.ref('purchase_stock.route_warehouse0_buy', raise_if_not_found=False)
            has_buy_route = buy_route and buy_route in line.product_id.route_ids
            
            # Vérifier si le produit a des fournisseurs configurés
            has_suppliers = bool(line.product_id.seller_ids)
            
            # Vérifier si le produit peut être acheté (champ standard)
            can_be_purchased = line.product_id.purchase_ok

            has_orderpoint = bool(self.env['stock.warehouse.orderpoint'].search_count([
                ('product_id', '=', line.product_id.id)
            ]))

            # Le produit a un réapprovisionnement configuré s'il peut être acheté ET a des fournisseurs
            has_replenishment = can_be_purchased and has_suppliers and has_orderpoint
            
            line.has_replenishment = has_replenishment
            
            if has_replenishment:
                line.replenishment_icon = '<i class="fa fa-refresh text-success" title="Replenishment configured"></i>'
            else:
                line.replenishment_icon = '<i class="fa fa-refresh text-danger" title="No replenishment configured"></i>'

