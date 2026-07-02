from odoo import models, fields, api, _

class VehicleBrand(models.Model):
    _name = 'vehicle.brand'
    _description = _('Vehicle brand')
    _order = 'name'
    _rec_name = 'name'

    name = fields.Char(
        string=_('Brand'),
        required=True,
        help=_('Brand of the vehicle')
    )
    
    active = fields.Boolean(
        string=_('Active'),
        default=True,
        help=_('Uncheck to archive the brand')
    )
    
    description = fields.Text(
        string=_('Description'),
        help=_('Description of the brand')
    )
    
    model_ids = fields.One2many(
        'vehicle.model',
        'brand_id',
        string=_('Models'),
        help=_('List of models of this brand')
    )
    
    model_count = fields.Integer(
        string=_('Model count'),
        compute='_compute_model_count',
        store=True
    )
    
    @api.depends('model_ids')
    def _compute_model_count(self):
        for brand in self:
            brand.model_count = len(brand.model_ids)
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', _('The brand name must be unique!'))
    ]