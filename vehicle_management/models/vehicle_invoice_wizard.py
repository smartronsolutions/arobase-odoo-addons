from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VehicleInvoiceWizard(models.TransientModel):
    _name = 'vehicle.invoice.wizard'
    _description = _('Invoice creation assistant with mileage statement')

    # Champs du wizard
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string=_('Vehicle'),
        required=True,
        readonly=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string=_('Client'),
        related='vehicle_id.partner_id',
        readonly=True
    )
    
    current_mileage = fields.Integer(
        string=_('Current mileage'),
        related='vehicle_id.current_mileage',
        readonly=True
    )
    
    # Champs obligatoires pour le nouveau relevé
    new_mileage = fields.Integer(
        string=_('New mileage'),
        required=True,
        help=_('Mileage recorded during this service')
    )
    
    mileage_date = fields.Date(
        string=_('Date'),
        required=True,
        default=fields.Date.today,
        help=_('Date on which the mileage was recorded')
    )
    
    notes = fields.Text(
        string=_('Notes'),
        help=_('Notes concerning this mileage')
    )
    
    # Champs pour la facture
    invoice_date = fields.Date(
        string=_('Invoice date'),
        default=fields.Date.today,
        required=True
    )
    
    
    @api.constrains('new_mileage', 'current_mileage')
    def _check_new_mileage(self):
        """Vérifier que le nouveau kilométrage est cohérent"""
        for wizard in self:
            if wizard.new_mileage <= wizard.current_mileage:
#                raise UserError(
#                    f"Le nouveau kilométrage ({wizard.new_mileage:,} km) doit être "
#                    f"supérieur au kilométrage actuel ({wizard.current_mileage:,} km)!"
#                )   
                raise UserError(_(
                    "The new mileage (%s km) must be "
                    "greater than the current mileage (%s km)!"
                ) % (
                    f"{wizard.new_mileage:,}",
                    f"{wizard.current_mileage:,}"
                ))


    def action_create_invoice(self):
        """Créer la facture avec le relevé kilométrique"""
        self.ensure_one()
        
        # 1. Créer le relevé kilométrique
        invoice_ref = self.invoice_ref or ''
        notes_text = self.notes or _("Mileage during billing %s") % invoice_ref

        mileage_vals = {
            'vehicle_id': self.vehicle_id.id,
            'date': self.mileage_date,
            'mileage': self.new_mileage,
#            'notes': self.notes or f"Relevé lors de facturation {self.invoice_ref or ''}",
            'notes': notes_text,
        }
        new_mileage = self.env['vehicle.mileage'].create(mileage_vals)
        
        # 2. Créer la facture
        invoice_vals = {
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'vehicle_id': self.vehicle_id.id,
            'vehicle_mileage_id': new_mileage.id,
            'invoice_date': self.invoice_date,
        }
        
        invoice = self.env['account.move'].create(invoice_vals)
        
        # 3. Lier le relevé à la facture
        new_mileage.invoice_id = invoice.id
        
        # 4. Message dans le chatter du véhicule
#        self.vehicle_id.message_post(
#            body=f"🧾 Facture créée : {invoice.name} "
#                 f"(Kilométrage : {self.new_mileage:,} km)",
#            subject="Facture créée"
#        )
        self.vehicle_id.message_post(
            body=_("🧾 Invoice created : %s (Mileage : %s km)") % (
                invoice.name,
                f"{self.new_mileage:,}"
            ),
            subject=_("Invoice created")
        )        

        # 5. Retourner l'action pour ouvrir la facture
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoice created'),
            'view_mode': 'form',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'target': 'current',
        }