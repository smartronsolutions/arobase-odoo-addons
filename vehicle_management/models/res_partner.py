from odoo import models, fields, api, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Champ de relation avec les véhicules
    vehicle_ids = fields.One2many(
        'vehicle.vehicle',
        'partner_id',
        string=_('Vehicles'),
        help=_('List of vehicles for this customer')
    )
    
    vehicle_count = fields.Integer(
        string=_('Vehicle count'),
        compute='_compute_vehicle_count',
    )
    
    @api.depends('vehicle_ids')
    def _compute_vehicle_count(self):
        for partner in self:
            partner.vehicle_count = len(partner.vehicle_ids)
    
    def action_view_vehicles(self):
        """Action pour voir les véhicules du client"""
        # Si un seul véhicule, ouvrir en mode formulaire
        if len(self.vehicle_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Vehicle'),
                'res_model': 'vehicle.vehicle',
                'view_mode': 'form',
                'res_id': self.vehicle_ids.id,
                'target': 'current',
            }
        else:
            # Sinon, afficher la liste filtrée
            return {
                'type': 'ir.actions.act_window',
                'name': _('Vehicles'),
                'res_model': 'vehicle.vehicle',
                'view_mode': 'tree,form',
                'domain': [('partner_id', '=', self.id)],
                'context': {
                    'default_partner_id': self.id,
                    'search_default_active': 1
                },
                'target': 'current',
            }
    
    # Méthode de recherche étendue pour inclure l'immatriculation
    @api.model
    def _name_search(self, name, domain=None, operator='ilike', limit=100, order=None):
        """Étendre la recherche pour inclure l'immatriculation des véhicules"""
        if domain is None:
            domain = []
        
        # Recherche normale d'abord
        partners = super()._name_search(name, domain, operator, limit, order)
        
        # Si pas de résultats et que le terme ressemble à une immatriculation
        if not partners and name and len(name) >= 3:
            # Rechercher par immatriculation de véhicule
            vehicles = self.env['vehicle.vehicle'].search([
                ('license_plate', operator, name)
            ], limit=limit)
            
            if vehicles:
                # Récupérer les clients propriétaires de ces véhicules
                partner_ids = vehicles.mapped('partner_id').ids
                partners = self.browse(partner_ids).name_get()
        
        return partners
