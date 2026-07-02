from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class SaleForceInvoiceWizard(models.TransientModel):
    _name = 'sale.force.invoice.wizard'
    _description = 'Wizard pour forcer le statut de facturation'
    
    sale_order_id = fields.Many2one(
        'sale.order', 
        string=_('Sale order'), 
        required=True, 
        readonly=True
    )
    
    current_status = fields.Selection(
        related='sale_order_id.invoice_status',
        readonly=True,
        string=_('Current status')
    )
    
    reason = fields.Text(
        string=_('Reason'),
        required=True,
    )
    
    @api.constrains('reason')
    def _check_reason_not_empty(self):
        """Vérifie que le motif n'est pas vide"""
        for record in self:
            if not record.reason or not record.reason.strip():
                raise ValidationError(_("The reason is required"))
    
    def action_confirm_force(self):
        """Confirme le forçage du statut"""
        self.ensure_one()
        if not self.reason or not self.reason.strip():
            raise ValidationError(_("The reason is required"))
        
        self.sale_order_id.force_invoice_status_with_reason(self.reason.strip())
        
        return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self):
        """Annule le wizard"""
        return {'type': 'ir.actions.act_window_close'}