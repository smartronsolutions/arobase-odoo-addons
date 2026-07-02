from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class VehicleMileage(models.Model):
    _name = 'vehicle.mileage'
    _description = _('Vehicle mileage')
    _order = 'date desc, id desc'
    _rec_name = 'display_name'

    # Champs principaux
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string=_('Vehicle'),
        required=True,
        ondelete='cascade',
        help=_('Vehicle related by this Mileage')
    )
    
    date = fields.Date(
        string=_('Date'),
        required=True,
        default=fields.Date.today,
        help=_('Date of the mileage')
    )
    
    mileage = fields.Integer(
        string=_('Mileage'),
        required=True,
        help=_('Mileage reading in kilometers')
    )
    
    notes = fields.Text(
        string=_('Notes'),
        help=_('Notes on this mileage (service, repair, etc.)')
    )
    
    user_id = fields.Many2one(
        'res.users',
        string=_('User'),
        default=lambda self: self.env.user,
        required=True,
        help=_('User who entered this mileage')
    )
    
    # Champs calculés
    display_name = fields.Char(
        string=_('Display name'),
        compute='_compute_display_name'
    )
    
    mileage_difference = fields.Integer(
        string=_('Mileage difference'),
        compute='_compute_mileage_difference',
        help=_('Difference from previous mileage')
    )
    
    partner_id = fields.Many2one(
        string=_('Client'),
        related='vehicle_id.partner_id',
        store=True
    )
    
    # Champ pour lien futur avec factures (étape 5)
    invoice_id = fields.Many2one(
        'account.move',
        string=_('Invoice related'),
        help=_('Invoice created during this mileage')
    )
    
    @api.depends('vehicle_id.license_plate', 'date', 'mileage')
    def _compute_display_name(self):
        for record in self:
            if record.vehicle_id and record.date:
                record.display_name = f"{record.vehicle_id.license_plate} - {record.date} ({record.mileage:,} km)"
            else:
                record.display_name = _('New mileage')
    
    @api.depends('mileage', 'vehicle_id', 'date')
    def _compute_mileage_difference(self):
        for record in self:
            record.mileage_difference = 0  # Valeur par défaut
            
            # Ne calculer que si l'enregistrement est sauvegardé
            if not record.id or not record.vehicle_id or not record.mileage or not record.date:
                continue
                
            # Chercher le relevé précédent
            previous_mileage = self.search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('date', '<', record.date),
                ('id', '!=', record.id)
            ], limit=1, order='date desc')
            
            if previous_mileage:
                record.mileage_difference = record.mileage - previous_mileage.mileage
    
    @api.constrains('mileage', 'vehicle_id', 'date')
    def _check_mileage_progression(self):
        """Vérifier que le kilométrage est cohérent"""
        for record in self:
            if record.mileage <= 0:
                raise ValidationError(_("The mileage must be positive!"))
            
            # Vérifier qu'il n'y a pas de recul kilométrique
            previous_mileage = self.search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('date', '<', record.date),
                ('id', '!=', record.id)
            ], limit=1, order='date desc')
            
            if previous_mileage and record.mileage < previous_mileage.mileage:
#                raise ValidationError(
#                    f"Le kilométrage ({record.mileage:,} km) ne peut pas être inférieur "
#                    f"au relevé précédent ({previous_mileage.mileage:,} km du {previous_mileage.date})!"
#                )
                raise ValidationError(_(
                    "The mileage (%s km) cannot be less than "
                    "the previous mileage (%s km du %s)!"
                ) % (
                    f"{record.mileage:,}",
                    f"{previous_mileage.mileage:,}",
                    previous_mileage.date
                ))

            # Vérifier qu'il n'y a pas de relevé futur avec un kilométrage inférieur
            future_mileage = self.search([
                ('vehicle_id', '=', record.vehicle_id.id),
                ('date', '>', record.date),
                ('id', '!=', record.id)
            ], limit=1, order='date asc')
            
            if future_mileage and record.mileage > future_mileage.mileage:
#                raise ValidationError(
#                    f"Le kilométrage ({record.mileage:,} km) ne peut pas être supérieur "
#                    f"au relevé suivant ({future_mileage.mileage:,} km du {future_mileage.date})!"
#                )
                raise ValidationError(_(
                    "The mileage (%s km) cannot be greater than "
                    "the futur mileage (%s km du %s)!"
                ) % (
                    f"{record.mileage:,}",
                    f"{future_mileage.mileage:,}",
                    future_mileage.date
                ))

    @api.model
    def create(self, vals):
        """Mettre à jour le kilométrage actuel du véhicule et logger"""
        record = super().create(vals)
        record._update_vehicle_current_mileage()
        
        # Logger dans le chatter du véhicule
        if record.vehicle_id:
            record.vehicle_id.message_post(
#                body=f"📊 Nouveau relevé kilométrique : {record.mileage:,} km "
#                    f"le {record.date} ({record.mileage_difference:+,} km)",
                body=_("📊 New mileage: %s km "
                    "on %s (%s km)") % (
                    f"{record.mileage:,}",
                    record.date,
                    f"{record.mileage_difference:+,}"
                ),
                subject=_("New mileage added")
            )
        return record

    def write(self, vals):
        """Logger les modifications de relevés"""
        old_values = {}
        for record in self:
            old_values[record.id] = {
                'mileage': record.mileage,
                'date': record.date
            }
        
        result = super().write(vals)
        
        # Logger les changements
        for record in self:
            changes = []
            
            # Vérifier changement de kilométrage
            if 'mileage' in vals and old_values[record.id]['mileage'] != record.mileage:
#                changes.append(f"kilométrage : {old_values[record.id]['mileage']:,} → {record.mileage:,} km")
                changes.append(_("mileage : %s → %s km") % (
                    f"{old_values[record.id]['mileage']:,}",
                    f"{record.mileage:,}"
                ))

            # Vérifier changement de date
            if 'date' in vals and old_values[record.id]['date'] != record.date:
#                changes.append(f"date : {old_values[record.id]['date']} → {record.date}")
                changes.append(_("date : %s → %s") % (
                    old_values[record.id]['date'],
                    record.date
                ))

            # Logger si il y a des changements
            if changes and record.vehicle_id:
                record.vehicle_id.message_post(
#                    body=f"📝 Relevé kilométrique modifié : {' | '.join(changes)}",
                    body=_("📝 Modified mileage : %s") % ' | '.join(changes),
                    subject=_("Modified mileage")
                )
            
            record._update_vehicle_current_mileage()
        
        return result
    
    def unlink(self):
        """Mettre à jour le kilométrage actuel du véhicule et logger la suppression"""
        # Sauvegarder les infos avant suppression pour le log
        deletion_logs = []
        for record in self:
            deletion_logs.append({
                'vehicle': record.vehicle_id,
                'mileage': record.mileage,
                'date': record.date,
                'user': self.env.user.name
            })
        
        vehicles_to_update = self.mapped('vehicle_id')
        result = super().unlink()
        
        # Logger dans le chatter après suppression
        for log_info in deletion_logs:
            if log_info['vehicle']:
                log_info['vehicle'].message_post(
#                    body=f"🗑️ Relevé kilométrique supprimé : {log_info['mileage']:,} km "
#                        f"(du {log_info['date']}) par {log_info['user']}",
                    body=_("🗑️ Mileage deleted : %s km "
                        "(on %s) by %s") % (
                        f"{log_info['mileage']:,}",
                        log_info['date'],
                        log_info['user']
                    ),
                    subject=_("Mileage deleted")
                )
        
        # Mettre à jour les kilométrages
        for vehicle in vehicles_to_update:
            vehicle._update_current_mileage()
        
        return result
    
    def _update_vehicle_current_mileage(self):
        """Mettre à jour le kilométrage actuel du véhicule"""
        self.ensure_one()
        if self.vehicle_id:
            self.vehicle_id._update_current_mileage()


#    def _compute_invoice_count(self):
#        for vehicle in self:
            # Maintenant implémenté correctement
#            vehicle.invoice_count = len(vehicle.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice'))