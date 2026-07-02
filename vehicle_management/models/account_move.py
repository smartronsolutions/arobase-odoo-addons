from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountMove(models.Model):
    _inherit = 'account.move'

    # Champ de relation avec le véhicule
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string=_('Vehicle'),
        tracking=True,
        help=_('Vehicle concerned by this invoice')
    )
    
    # Champ pour le relevé kilométrique associé
    vehicle_mileage_id = fields.Many2one(
        'vehicle.mileage',
        string=_('Mileage'),
        readonly=True,
        help=_('Mileage recorded at the time of this invoice')
    )
    
    # Champs calculés pour affichage
    vehicle_license_plate = fields.Char(
        string=_('Licence plate'),
        related='vehicle_id.license_plate',
        readonly=True
    )
    
#    vehicle_mileage = fields.Integer(
#        string='Kilométrage facturé',
#        related='vehicle_mileage_id.mileage',
#        readonly=True
#    )

    vehicle_mileage_value = fields.Integer(
        string=_('Mileage Value'),
        help=_('Mileage value during this service')
    )

    vehicle_current_mileage = fields.Integer(
        string=_('Current mileage'),
        related='vehicle_id.current_mileage',
        readonly=True
    )


#    @api.onchange('vehicle_id')
#    def _onchange_vehicle_id(self):
#        """Pré-remplir le client quand on sélectionne un véhicule"""
#        if self.vehicle_id:
#            self.partner_id = self.vehicle_id.partner_id
            # Pré-remplir le nom de la facture
#            self.ref = f"Intervention {self.vehicle_id.license_plate}"

    @api.onchange('partner_id')
    def _onchange_partner_id_vehicle(self):
        """Vider le véhicule quand on change de client"""
        if self.partner_id:
            self.vehicle_id = False
            self.vehicle_license_plate = ""

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Actions quand on sélectionne un véhicule"""
        if self.vehicle_id:
            # Pré-remplir le client si pas encore fait
            if not self.partner_id:
                self.partner_id = self.vehicle_id.partner_id
            
            # Vider le kilométrage pour nouvelle saisie
            self.vehicle_mileage_value = 0
            
            # Pré-remplir la référence
#            if not self.ref:
#                self.ref = f"Intervention {self.vehicle_id.license_plate}"
        else:
            self.vehicle_mileage_value = 0

    @api.constrains('vehicle_mileage_value', 'vehicle_id')
    def _check_vehicle_mileage(self):
        """Vérifier la cohérence du kilométrage"""
        for invoice in self:
            if invoice.vehicle_id and invoice.vehicle_mileage_value:
                if invoice.vehicle_mileage_value <= invoice.vehicle_current_mileage:
#                    raise ValidationError(
#                        f"Le kilométrage saisi ({invoice.vehicle_mileage_value:,} km) doit être "
#                        f"supérieur au kilométrage actuel ({invoice.vehicle_current_mileage:,} km) "
#                        f"du véhicule {invoice.vehicle_id.license_plate}!"
#                    )
                    raise ValidationError(_(
                        "The mileage value (%s km) must be "
                        "greater than the current mileage (%s km) "
                        "of the vehicle %s!"
                    ) % (
                        f"{invoice.vehicle_mileage_value:,}",
                        f"{invoice.vehicle_current_mileage:,}",
                        invoice.vehicle_id.license_plate
                    ))


    def action_post(self):
        """Créer le relevé kilométrique lors de la validation de la facture"""
        result = super().action_post()
        
        for invoice in self:
            # Créer le relevé seulement pour les factures client avec véhicule et kilométrage
            if (invoice.move_type == 'out_invoice' and 
                invoice.vehicle_id and 
                invoice.vehicle_mileage_value and 
                not invoice.vehicle_mileage_id):
                
                # Créer le relevé kilométrique
                invoice_ref = invoice.name or invoice.ref or ''
                mileage_vals = {
                    'vehicle_id': invoice.vehicle_id.id,
                    'date': invoice.invoice_date or fields.Date.today(),
                    'mileage': invoice.vehicle_mileage_value,
#                    'notes': f"Relevé lors de facturation {invoice.name or invoice.ref or ''}",
                    'notes': _("Mileage value at the time of billing %s") % invoice_ref,
                    'invoice_id': invoice.id,
                }
                
                mileage_record = self.env['vehicle.mileage'].create(mileage_vals)
                invoice.vehicle_mileage_id = mileage_record.id
                
                # Message dans le chatter du véhicule
                invoice.vehicle_id.message_post(
#                    body=f"🧾 Facture validée : {invoice.name} "
#                         f"(Kilométrage : {invoice.vehicle_mileage_value:,} km)",
                    body=_("🧾 Invoice validated : %s (Mileage : %s km)") % (
                        invoice.name,
                        f"{invoice.vehicle_mileage_value:,}"
                    ),
                    subject=_("Invoice validated with recorded mileage")
                )
        
        return result
    
    def button_cancel(self):
        """Supprimer le relevé si la facture est annulée"""
        # Sauvegarder les relevés à supprimer
        mileage_to_delete = self.mapped('vehicle_mileage_id').filtered(lambda m: m.invoice_id)
        
        result = super().button_cancel()
        
        # Supprimer les relevés associés
        if mileage_to_delete:
            mileage_to_delete.unlink()
        
        return result