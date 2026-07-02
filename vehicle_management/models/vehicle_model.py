from odoo import models, fields, api, _

class VehicleModel(models.Model):
    _name = 'vehicle.model'
    _description = _('Vehicle model')
    _order = 'brand_id, name'
    _rec_name = 'display_name'

    name = fields.Char(
        string=_('Model'),
        required=True,
        help=_('Model of the vehicle')
    )
    
    brand_id = fields.Many2one(
        'vehicle.brand',
        string=_('Brand'),
        required=True,
        ondelete='cascade',
        help=_('Brand of the vehicle')
    )
    
    active = fields.Boolean(
        string=_('Active'),
        default=True,
        help=_('Uncheck to archive model')
    )
    
    description = fields.Text(
        string=_('Description'),
        help=_('Description of the model')
    )
    
    display_name = fields.Char(
        string=_('Complete name'),
        compute='_compute_display_name',
        store=True
    )
    
    vehicle_count = fields.Integer(
        string=_('Vehicle count'),
        compute='_compute_vehicle_count'
    )
    
    @api.depends('name', 'brand_id.name')
    def _compute_display_name(self):
        for model in self:
            if model.brand_id:
                model.display_name = f"{model.brand_id.name} {model.name}"
            else:
                model.display_name = model.name
    
    def _compute_vehicle_count(self):
        for model in self:
            model.vehicle_count = self.env['vehicle.vehicle'].search_count([
                ('model_id', '=', model.id)
            ])
    
    _sql_constraints = [
        ('name_brand_unique', 'UNIQUE(name, brand_id)', 
         _('This model already exists for this brand!'))
    ]