from odoo import models, fields, api, _

from odoo import models, fields, api, _

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    # Champ calculé pour compter les Sale Orders liées
    sale_order_count = fields.Integer(
        string=_('Sale Orders Count'),
        compute='_compute_sale_order_count',
        store=True,
        help=_('Number of sale orders linked to this purchase order')
    )
    
    # Liste des Sale Orders liées (pour debug)
    sale_order_names = fields.Char(
        string=_('Related Sale Orders'),
        compute='_compute_sale_order_count',
        store=True,
        help=_('Names of related sale orders')
    )
    
    @api.depends('origin')
    def _compute_sale_order_count(self):
        """Utilise la MÊME logique que votre Sale Order mais en sens inverse"""
        for order in self:
            sale_orders = self.env['sale.order']
            
            # Méthode 1: Chercher les SO qui ont ce PO dans leur purchase_order_ids
            # En utilisant votre logique : SO cherche PO via origin, donc PO doit chercher SO qui le référence
            
            # Recherche des SO qui trouvent ce PO via leur méthode _compute_purchase_orders
            all_sale_orders = self.env['sale.order'].search([])
            for so in all_sale_orders:
                # Forcer le recalcul des PO liés pour ce SO
                so._compute_purchase_orders()
                # Vérifier si ce PO est dans les PO liés
                if order.id in so.purchase_order_ids.ids:
                    sale_orders |= so
            
            # Alternative plus efficace : chercher les SO dont le nom est dans origin de ce PO
            if not sale_orders and order.origin:
                origin_parts = [part.strip() for part in order.origin.split(',')]
                for part in origin_parts:
                    if part and not part.startswith('PO'):  # Éviter les références PO
                        sale_order = self.env['sale.order'].search([
                            ('name', '=', part)
                        ], limit=1)
                        if sale_order:
                            sale_orders |= sale_order
            
            # Méthode 3: Via procurement group (même logique que votre SO)
            if not sale_orders:
                po_moves = self.env['stock.move'].search([
                    ('purchase_line_id.order_id', '=', order.id)
                ])
                
                for move in po_moves:
                    if move.group_id:
                        group_moves = self.env['stock.move'].search([
                            ('group_id', '=', move.group_id.id),
                            ('sale_line_id', '!=', False)
                        ])
                        for group_move in group_moves:
                            if group_move.sale_line_id:
                                sale_orders |= group_move.sale_line_id.order_id
            
            order.sale_order_count = len(sale_orders)
            order.sale_order_names = ', '.join(sale_orders.mapped('name')) if sale_orders else ''
    
#    def action_view_linked_sale_orders(self):
    def action_view_sale_orders(self):
        """Action pour voir les Sale Orders liées"""
        self.ensure_one()
        
        # Force le recalcul
        self._compute_sale_order_count()
        
        # Récupérer les Sale Orders
        if self.sale_order_names:
            so_names = [name.strip() for name in self.sale_order_names.split(',')]
            sale_orders = self.env['sale.order'].search([
                ('name', 'in', so_names)
            ])
        else:
            sale_orders = self.env['sale.order']
        
        if not sale_orders:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('No linked sale orders found.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        if len(sale_orders) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Related Sale Order'),
                'res_model': 'sale.order',
                'res_id': sale_orders.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related Sale Orders'),
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', sale_orders.ids)],
            'target': 'current',
        }