from odoo import models, fields, api, _

class VehicleVehicle(models.Model):
    _name = 'vehicle.vehicle'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = _('Custome vehicle')
    _order = 'partner_id, brand_id, model_id'
    _rec_name = 'display_name'

    # Champs de base
    name = fields.Char(
        string=_('Name of the vehicle'),
        help=_('Name of the vehicle')
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string=_('Client'),
        required=True,
        ondelete='cascade',
        tracking=True,
        help=_('Vehicle owner customer')
    )
    
    brand_id = fields.Many2one(
        'vehicle.brand',
        string=_('Brand'),
        required=True,
        ondelete='restrict',
        tracking=True,
        help=_('Brand of the vehicle')
    )
    
    model_id = fields.Many2one(
        'vehicle.model',
        string=_('Model'),
        required=True,
        ondelete='restrict',
        tracking=True,
        help=_('Model of the vehicle')
    )
    
    # Identification du véhicule
    license_plate = fields.Char(
        string=_('Licence plate'),
        required=True,
        tracking=True,
        help=_('Licence plate of the vehicle')
    )
    
    vin = fields.Char(
        string=_('Vehicle Identification Number (VIN)'),
        help=_('Vehicle Identification Number (VIN)')
    )
    
    # Caractéristiques techniques
    year = fields.Integer(
        string=_('Year of the model'),
        help=_('Year of the model')
    )
    
    engine = fields.Char(
        string=_('Engine'),
        help=_('Engine type')
    )
    
    transmission = fields.Selection([
        ('manual', _('Manual')),
        ('automatic', _('Automatic')),
        ('semi_automatic', _('Semi-automatic'))
    ], string=_('Transmission'), help=_('Type of transmission'))
    
    fuel_type = fields.Selection([
        ('gasoline', _('Gasoline')),
        ('diesel', _('Diesel')),
        ('electric', _('Electric')),
        ('hybrid', _('Hybrid')),
        ('other', _('Other'))
    ], string=_('Fuel'), help=_('Fuel type'))
    
    # Caractéristiques physiques
    doors = fields.Selection([
        ('3', _('3 doors')),
        ('5', _('5 doors'))
    ], string=_('Doors count'))
    
    seats = fields.Integer(
        string=_('Number of seats'),
        help=_('Number of seats')
    )
    
    # Kilométrage
    current_mileage = fields.Integer(
        string=_('Mileage'),
        tracking=True,
        readonly=True,
        help=_('Last mileage reading')
    )
    
    # Informations administratives
    first_registration = fields.Date(
        string=_('Date of vehicle registration'),
        tracking=True,
        help=_('Date of vehicle registration')
    )
    
    circulation_date = fields.Date(
        string=_('Circulation date'),
        tracking=True,
        help=_('Circulation date of the vehicle')
    )
    
    # Statut et informations diverses
    active = fields.Boolean(
        string=_('Active'),
        default=True,
        help=_('Uncheck to archive the vehicle')
    )
    
    notes = fields.Text(
        string=_('Notes'),
        help=_('Notes')
    )
    
    # Champs calculés
    display_name = fields.Char(
        string=_('Display name'),
        compute='_compute_display_name',
        store=True
    )


    mileage_ids = fields.One2many(
        'vehicle.mileage',
        'vehicle_id',
        string=_('Mileage history'),
        help=_('Mileage history')
    )
    
    mileage_count = fields.Integer(
        string=_('Mileage count'),
        compute='_compute_mileage_count'
    )
    
    last_mileage_date = fields.Date(
        string=_('Last mileage date'),
        compute='_compute_last_mileage_info'
    )    

    invoice_ids = fields.One2many(
        'account.move',
        'vehicle_id',
        string=_('Invoices'),
        domain=[('move_type', '=', 'out_invoice')]
    )
    
    invoice_count = fields.Integer(
        string=_('Invoice count'),
        compute='_compute_invoice_count'
    )
    
    @api.depends('name', 'brand_id.name', 'model_id.name', 'license_plate')
    def _compute_display_name(self):
        for vehicle in self:
            parts = []
            if vehicle.license_plate:
                parts.append(vehicle.license_plate)
            if vehicle.brand_id:
                parts.append(vehicle.brand_id.name)
            if vehicle.model_id:
                parts.append(vehicle.model_id.name)
            if vehicle.name:
                parts.append(f"({vehicle.name})")
            # Construire le nom avec des séparateurs appropriés
            if len(parts) >= 2:
                # Première partie (immatriculation) + " - " + reste
                vehicle.display_name = parts[0] + " - " + " ".join(parts[1:])
            elif parts:
                vehicle.display_name = parts[0]
            else:
                vehicle.display_name = _('New vehicle')
    

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        """Vider le modèle quand on change de marque"""
        if self.brand_id:
            self.model_id = False
            return {
                'domain': {
                    'model_id': [('brand_id', '=', self.brand_id.id)]
                }
            }
        else:
            return {
                'domain': {
                    'model_id': []
                }
            }


    @api.depends('mileage_ids')
    def _compute_mileage_count(self):
        for vehicle in self:
            vehicle.mileage_count = len(vehicle.mileage_ids)
    
    @api.depends('mileage_ids.date', 'mileage_ids.mileage')
    def _compute_last_mileage_info(self):
        for vehicle in self:
            last_mileage = vehicle.mileage_ids.filtered(lambda m: m.date).sorted('date', reverse=True)[:1]
            if last_mileage:
                vehicle.last_mileage_date = last_mileage.date
            else:
                vehicle.last_mileage_date = False
    
    def _update_current_mileage(self):
        """Mettre à jour le kilométrage actuel basé sur le dernier relevé"""
        self.ensure_one()
        last_mileage = self.mileage_ids.filtered(lambda m: m.date).sorted('date', reverse=True)[:1]
        if last_mileage:
            self.current_mileage = last_mileage.mileage
        else:
            self.current_mileage = 0
    
    def action_view_mileage_history(self):
        """Action pour voir l'historique kilométrique"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Mileage history'),
            'res_model': 'vehicle.mileage',
            'view_mode': 'tree,form',
            'domain': [('vehicle_id', '=', self.id)],
            'context': {
                'default_vehicle_id': self.id,
            },
            'target': 'current',
        }


    @api.depends('invoice_ids')
    def _compute_invoice_count(self):
        for vehicle in self:
            vehicle.invoice_count = len(vehicle.invoice_ids.filtered(lambda inv: inv.move_type == 'out_invoice'))
    
    def action_view_invoices(self):
        """Action pour voir les factures du véhicule"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Invoices'),
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'domain': [('vehicle_id', '=', self.id), ('move_type', '=', 'out_invoice')],
            'context': {
                'default_vehicle_id': self.id,
                'default_partner_id': self.partner_id.id,
                'default_move_type': 'out_invoice'
            },
            'target': 'current',
        }
    
#    def action_create_invoice_with_mileage(self):
#        """Ouvrir le wizard de création facture avec relevé kilométrique"""
#        return {
#            'type': 'ir.actions.act_window',
#            'name': 'Créer une facture',
#            'view_mode': 'form',
#            'res_model': 'vehicle.invoice.wizard',
#            'target': 'new',
#            'context': {
#                'default_vehicle_id': self.id,
#            }
#        }

    _sql_constraints = [
        ('license_plate_unique', 'UNIQUE(license_plate)', 
         _('This licence plate already exist!')),
        ('vin_unique', 'UNIQUE(vin)', 
         _('This Vehicle Identification Number already exist!')),
        ('year_check', 'CHECK(year >= 1900)', 
         _('The model year cannot be earlier than 1900!')),
        ('mileage_positive', 'CHECK(current_mileage >= 0)', 
         _('Mileage cannot be negative!'))
    ]
    
    compatibility_category_ids = fields.Many2many(
        'compatibility.category',
        'vehicle_compatibility_rel',  # relation table
        'vehicle_id',
        'category_id',
        string="Compatibility Category"
    )