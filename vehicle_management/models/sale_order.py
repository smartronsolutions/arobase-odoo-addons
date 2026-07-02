from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Champ véhicule unique
    vehicle_id = fields.Many2one(
        'vehicle.vehicle',
        string=_('Vehicle'),
        domain="[('partner_id', '=', partner_id)]",
        tracking=True,
        help=_('Vehicle related by this sale order')
    )
    
    vehicle_compatibility_text = fields.Char(
        string="Vehicle Compatibility",
        compute="_compute_vehicle_compatibility",
        store=True
    )
    
    def _get_action_add_from_catalog_extra_context(self):
        """
        Overrides the catalog context to auto-fill the 'compatibility_search_text'
        filter defined in the product search view.
        """
        # Get the standard context
        res = super()._get_action_add_from_catalog_extra_context()
        
        # Check if a vehicle and compatibility categories exist
        if self.vehicle_id and self.vehicle_id.compatibility_category_ids:
            # Use the complete name of the compatibility category
            # e.g., "Supra / Mazda / 2020 - 2026 / latest / New Var"
            compatibility_text = self.vehicle_id.compatibility_category_ids[0].complete_name
            
            # KEY CHANGE: Target your specific field 'compatibility_search_text'
            # This will trigger the "Search Compatibility for: ..." option automatically.
            res['search_default_compatibility_search_text'] = compatibility_text
            
        return res

    @api.depends('vehicle_id', 'vehicle_id.compatibility_category_ids')
    def _compute_vehicle_compatibility(self):
        for rec in self:
            if rec.vehicle_id and rec.vehicle_id.compatibility_category_ids:
                comp = rec.vehicle_id.compatibility_category_ids[0]
                rec.vehicle_compatibility_text = comp.complete_name
            else:
                rec.vehicle_compatibility_text = ""

#     @api.depends('vehicle_id', 'vehicle_id.compatibility_category_ids')
#     def _compute_vehicle_compatibility(self):
#         for rec in self:
#             if rec.vehicle_id and rec.vehicle_id.compatibility_category_ids:
#                 comp = rec.vehicle_id.compatibility_category_ids[0]

#                 rec.vehicle_compatibility_text = """
#                     This vehicle <b>{}</b> compatibility is <b>{}</b>
#                 """.format(
#                     rec.vehicle_id.display_name,
#                     comp.complete_name
#                 )
#             else:
#                 rec.vehicle_compatibility_text = ""
    
    # Champ related pour affichage de l'immatriculation
    vehicle_license_plate = fields.Char(
        string=_('Licence plate'),
        related='vehicle_id.license_plate',
        readonly=True
    )
    
    @api.onchange('partner_id')
    def _onchange_partner_id_vehicle(self):
        """Vider le véhicule quand on change de client"""
        result = super()._onchange_partner_id()
        if self.partner_id:
            self.vehicle_id = False
        return result
    
    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Pré-remplir le client si pas encore fait"""
        if self.vehicle_id and not self.partner_id:
            self.partner_id = self.vehicle_id.partner_id

    @api.onchange('vehicle_id')
    def _onchange_vehicle_id(self):
        """Pré-remplir le client si pas encore fait"""
        if self.vehicle_id and not self.partner_id:
            self.partner_id = self.vehicle_id.partner_id

    def _prepare_invoice(self):
        """Transférer le véhicule vers la facture"""
        invoice_vals = super()._prepare_invoice()
        
        # Ajouter le véhicule à la facture
        if self.vehicle_id:
            invoice_vals.update({
                'vehicle_id': self.vehicle_id.id,
                'vehicle_license_plate': self.vehicle_id.license_plate,
            })
        
        return invoice_vals