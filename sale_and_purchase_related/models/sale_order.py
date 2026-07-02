from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    # Champs calculés basés sur la traçabilité stock existante
    purchase_order_ids = fields.Many2many(
        'purchase.order',
        string=_('Related Purchase Orders'),
        compute='_compute_purchase_orders',
        help=_('Purchase orders related to this sales order via stock moves')
    )
    
    purchase_order_count = fields.Integer(
        string=_('Purchase Order Count'),
        compute='_compute_purchase_orders',
    )
    
    # Nouveaux statuts
    purchase_status = fields.Selection([
        ('no_purchase', _('No Purchase')),
        ('purchase_pending', _('Purchase Pending')),
        ('purchase_validated', _('Purchase Validated')),
        ('purchase_cancelled', _('Purchase Cancelled')),
    ], string=_('Purchase Status'), 
       default='no_purchase',
       compute='_compute_purchase_status',
       store=True,
       help=_('Status of related purchase orders'))


    @api.depends('name')  # Simplification pour forcer le recalcul
    def _compute_purchase_orders(self):
        """Compute purchase orders via stock move traceability"""
        for order in self:
            purchase_orders = self.env['purchase.order']
            
            # Version simplifiée : recherche via origin
            purchase_orders = self.env['purchase.order'].search([
                ('origin', 'ilike', order.name)
            ])
            
            # Si pas trouvé, essayer via procurement group
            if not purchase_orders and order.procurement_group_id:
                group_moves = self.env['stock.move'].search([
                    ('group_id', '=', order.procurement_group_id.id),
                    ('purchase_line_id', '!=', False)
                ])
                for move in group_moves:
                    if move.purchase_line_id:
                        purchase_orders |= move.purchase_line_id.order_id
            
            order.purchase_order_ids = purchase_orders
            order.purchase_order_count = len(purchase_orders)
            
            # CORRECTION 1: Appeler la méthode de statut
            order._compute_purchase_status()
    
    def _compute_purchase_status(self):
        """Compute purchase status based on linked purchase orders"""
        for record in self:
            if not record.purchase_order_ids:
                record.purchase_status = 'no_purchase'
                continue
                
            po_states = record.purchase_order_ids.mapped('state')
            
            # Séparer les PO actifs et annulés
            active_po_states = [state for state in po_states if state != 'cancel']
            cancelled_po_states = [state for state in po_states if state == 'cancel']
            
            # Si tous les PO sont annulés
            if not active_po_states and cancelled_po_states:
                record.purchase_status = 'purchase_cancelled'
                continue
            
            # S'il n'y a aucun PO (ni actif ni annulé)
            if not active_po_states and not cancelled_po_states:
                record.purchase_status = 'no_purchase'
                continue
            
            # Si au moins un PO est en attente (draft, sent, to approve)
            pending_states = ['draft', 'sent', 'to approve']
            if any(state in pending_states for state in active_po_states):
                record.purchase_status = 'purchase_pending'
            
            # Si tous les PO actifs sont purchase ou done -> purchase_validated
            elif all(state in ['purchase', 'done'] for state in active_po_states):
                record.purchase_status = 'purchase_validated'
            
            # Cas par défaut
            else:
                record.purchase_status = 'purchase_pending'
    
#    def action_view_linked_purchase_orders(self):
    def action_view_purchase_orders(self):
        """Action to view linked purchase orders"""
        self.ensure_one()
        
        if not self.purchase_order_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('No linked purchase orders found.'),
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        if len(self.purchase_order_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Related Purchase Order'),
                'res_model': 'purchase.order',
                'res_id': self.purchase_order_ids.id,
                'view_mode': 'form',
                'target': 'current',
            }
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Related Purchase Orders'),
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.purchase_order_ids.ids)],
            'target': 'current',
        }