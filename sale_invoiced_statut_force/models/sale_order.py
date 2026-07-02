from odoo import models, fields, api, _
from odoo.exceptions import UserError
from markupsafe import Markup

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_invoice_status_forced = fields.Boolean(
        string="Invoice Status Forced",
        default=False,
        help="Indicates if the invoice status has been manually forced"
    )

    def action_force_invoiced_status(self):
        """Force le statut de facturation à 'invoiced' avec wizard de justification"""
        self.ensure_one()
        if self.state not in ['sale', 'done']:
            raise UserError(_("The order must be in sale order to force the invoice status."))

        if self.invoice_status == 'invoiced':
            raise UserError(_("This order is already marked as 'Fully invoiced'."))

        return {
            'type': 'ir.actions.act_window',
            'name': _('Force invoice status on "Fully invoiced"'),
            'res_model': 'sale.force.invoice.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_sale_order_id': self.id}
        }
    
    def action_reset_invoice_status(self):
        """Recalcule le statut de facturation basé sur les factures réelles"""
        self.ensure_one()
        old_status = self.invoice_status
        old_status_label = dict(self._fields['invoice_status'].selection).get(old_status, old_status)
        
        self.is_invoice_status_forced = False
        self._compute_invoice_status()
        
        new_status_label = dict(self._fields['invoice_status'].selection).get(self.invoice_status, self.invoice_status)
        
        # Message dans le chatter
        self._post_reset_status_message(old_status_label, new_status_label)
    
    def force_invoice_status_with_reason(self, reason):
        """Force le statut avec traçabilité dans le chatter"""
        old_status = self.invoice_status
        old_status_label = dict(self._fields['invoice_status'].selection).get(old_status, old_status)
        
        self.invoice_status = 'invoiced'
        self.is_invoice_status_forced = True
        
        # Message dans le chatter
        self._post_force_status_message(old_status_label, reason)
    
    def _post_force_status_message(self, old_status_label, reason):
        """Poste le message de forçage dans le chatter"""
        if not self.exists():
            return
            
        # Construction du message SANS f-strings pour permettre les traductions
        message_parts = []
        message_parts.append("<p><strong>⚠️ %s</strong></p>" % _('Invoice status force on "Fully invoiced"'))
        message_parts.append("<p>- %s: %s</p>" % (_('Old status'), old_status_label))
        message_parts.append("<p>- %s: %s</p>" % (_('New status'), _('Fully invoiced')))
        message_parts.append("<p>- %s: %s</p>" % (_('Reason'), reason))
        message_parts.append("<p>- %s: %s</p>" % (_('Date'), fields.Datetime.context_timestamp(self, fields.Datetime.now()).strftime('%d/%m/%Y %H:%M')))
        message_parts.append("")
        
        # Joindre toutes les parties avec Markup
        message_body = Markup("".join(message_parts))
        
        # Poster le message dans le chatter
        self.message_post(
            body=message_body,
            subject=_("Invoice status force: %s") % self.name,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )
    
    def _post_reset_status_message(self, old_status_label, new_status_label):
        """Poste le message de recalcul dans le chatter"""
        if not self.exists():
            return
            
        # Construction du message SANS f-strings pour permettre les traductions
        message_parts = []
        message_parts.append("<p><strong>🔄 %s</strong></p>" % _('Reset invoice status'))
        message_parts.append("<p>- %s: %s</p>" % (_('Old status'), old_status_label))
        message_parts.append("<p>- %s: %s</p>" % (_('New status'), new_status_label))
        message_parts.append("<p>- %s: %s</p>" % (_('Date'), fields.Datetime.context_timestamp(self, fields.Datetime.now()).strftime('%d/%m/%Y %H:%M')))
        message_parts.append("")
        message_parts.append("<p><em>%s</em></p>" % _('The invoice status is automatically recalculate based on the invoices that were actually created.'))
        
        # Joindre toutes les parties avec Markup
        message_body = Markup("".join(message_parts))
        
        # Poster le message dans le chatter
        self.message_post(
            body=message_body,
            subject=_("Invoice status reset: %s") % self.name,
            message_type='notification',
            subtype_xmlid='mail.mt_note'
        )