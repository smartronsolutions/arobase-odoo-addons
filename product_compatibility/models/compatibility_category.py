# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class CompatibilityCategory(models.Model):
    """Catégories de compatibilité (parallèle aux catégories produit natives)"""
    _name = 'compatibility.category'
    _description = 'Catégorie de compatibilité'
    _parent_store = True
    _rec_name = 'name'
#    _rec_name = 'complete_name'
    _order = 'complete_name'


    """Override name field"""
    name = fields.Char(_('Name'), required=False, translate=True, readonly=False)

    # Many2one fields for hierarchy
    brand_id = fields.Many2one('vehicle.brands', string=_("Brand"), index=True)
    model_id = fields.Many2one(
        'vehicle.models',
        string=_("Model"),
        domain="[('brand_id', '=', brand_id)]",
        index=True
    )
    year_id = fields.Many2one(
        'vehicle.years',
        string=_("Year"),
        domain="[('model_id', '=', model_id)]",
        index=True
    )
    series_id = fields.Many2one(
        'vehicle.serieses',
        string=_("Series"),
        domain="[('year_id', '=', year_id)]",
        index=True
    )
    variant_id = fields.Many2one(
        'vehicle.variants',
        string=_("Variant"),
        domain="[('series_id', '=', series_id)]",
        index=True
    )

    # Computed full path
    vehicle_path = fields.Char(
        string=_('Complete Name'),
        compute='_compute_vehicle_path',
        store=True,
        index=True,
        help=_("Format: BRAND / MODEL / YEAR / SERIES / VARIANT")
    )

    @api.depends('brand_id', 'model_id', 'year_id', 'series_id', 'variant_id')
    def _compute_vehicle_path(self):
        for rec in self:
            parts = [
                rec.brand_id.name if rec.brand_id else None,
                rec.model_id.name if rec.model_id else None,
                rec.year_id.name if rec.year_id else None,
                rec.series_id.name if rec.series_id else None,
                rec.variant_id.name if rec.variant_id else None,
            ]
            rec.vehicle_path = ' / '.join([p for p in parts if p])
            if rec.vehicle_path:
                rec.name = rec.vehicle_path


    # Check unique name compatibility
    @api.constrains('vehicle_path')
    def _check_unique_vehicle_path(self):
        """Vérifier que le chemin véhicule est unique"""
        for record in self:
            if record.vehicle_path:
                domain = [
                    ('vehicle_path', '=', record.vehicle_path),
                    ('id', '!=', record.id)
                ]
                existing = self.search(domain, limit=1)
                if existing:
                    raise ValidationError(
                        _('A vehicle with the path "%s" already exists.') % record.vehicle_path
                    )


    complete_name = fields.Char(
        _('Complete name'), 
        compute='_compute_complete_name', 
        recursive=True, 
        store=True
    )
    
    # Hiérarchie
    parent_id = fields.Many2one(
        'compatibility.category', 
        string=_("Parent category"), 
        index=True, 
        ondelete='cascade'
    )
    parent_path = fields.Char(index=True)

    child_ids = fields.One2many(
        'compatibility.category', 
        'parent_id', 
        string=_("Child category")
    )
    
    # Informations supplémentaires
    sequence = fields.Integer(string=_("Sequence"), default=10, help=_("Display order"))
    active = fields.Boolean(string=_("Active"), default=True)
    description = fields.Text(string=_("Description"))
    
    # Relations avec les produits
    product_ids = fields.Many2many(
        'product.template', 
        'product_compatibility_category_rel',
        'category_id', 'product_id', 
        string=_('Compatible products')
    )
    
    # Compteurs
    product_count = fields.Integer(
        string=_("Product count"), 
        compute='_compute_product_count'
    )


    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for record in self:
            if record.parent_id:
                record.complete_name = "%s / %s" % (record.parent_id.complete_name, record.name)
            else:
                record.complete_name = record.name

#    @api.depends('product_ids', 'child_ids.product_count')
#    def _compute_product_count(self):
#        for record in self:
            # Produits directs
#            direct_count = len(record.product_ids)
            # Produits des catégories enfants (récursif)
#            child_count = sum(child.product_count for child in record.child_ids)
#            record.product_count = direct_count + child_count


    @api.depends('product_ids', 'child_ids.product_count')
    def _compute_product_count(self):
        for record in self:
            # Vérifier si l'enregistrement existe en base
            if not record.id or isinstance(record.id, type(record.env['compatibility.category'].new().id)):
                # Nouvel enregistrement : compter seulement les produits directs
                record.product_count = len(record.product_ids)
            else:
                # Enregistrement existant : compter récursivement
                all_categories = record.search([('id', 'child_of', record.id)])
                all_products = all_categories.mapped('product_ids')
                record.product_count = len(all_products)

#    @api.depends('product_ids', 'child_ids.all_product_count')
#    def _compute_all_product_count(self):
#        for record in self:
            # Produits directs
#            direct_count = len(record.product_ids)
            # Produits des catégories enfants
#            child_count = sum(child.all_product_count for child in record.child_ids)
#            record.all_product_count = direct_count + child_count

    @api.constrains('parent_id')
    def _check_category_recursion(self):
        """Vérifier qu'il n'y a pas de récursion dans la hiérarchie"""
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot create recursive categories.'))

    @api.model
    def name_create(self, name):
        """Permet la création rapide de catégories depuis l'interface"""
        return self.create({'name': name}).name_get()[0]

    def name_get(self):
        """Affichage du nom complet dans les listes déroulantes"""
        result = []
        for record in self:
            result.append((record.id, record.complete_name))
        return result

    def action_view_products(self):
        """Action pour voir tous les produits (directs + enfants)"""
        # Récupérer toutes les catégories enfants + cette catégorie
        all_categories = self.search([('id', 'child_of', self.ids)])
        all_products = all_categories.mapped('product_ids')
        
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Compatible products'),
            'res_model': 'product.template',
            'view_mode': 'tree,kanban,form',
        }
        
        if len(all_products) > 1:
            action['domain'] = [('id', 'in', all_products.ids)]
        elif len(all_products) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = all_products.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        return action

    def get_children_categories(self, include_self=True):
        """Récupérer toutes les catégories enfants"""
        domain = [('id', 'child_of', self.ids)]
        if not include_self:
            domain.append(('id', 'not in', self.ids))
        return self.search(domain)

    def get_parent_categories(self, include_self=True):
        """Récupérer toutes les catégories parentes"""
        domain = [('id', 'parent_of', self.ids)]
        if not include_self:
            domain.append(('id', 'not in', self.ids))
        return self.search(domain)


    # Nouveau 02.08.25 pour nouveau modele compatibilite product_compatibility_views
    def write(self, vals):
        """Override write pour mettre à jour les champs dénormalisés"""
        result = super().write(vals)
        
        # Si le nom change, mettre à jour les relations liées
        if 'name' in vals or 'parent_id' in vals:
            for category in self:
                relations = self.env['product.compatibility.view'].search([('category_id', '=', category.id)])
                # Forcer le recalcul des champs relatifs
                relations._compute_display_name()
                relations._compute_search_text()
        
        return result

    def unlink(self):
        """Override unlink pour nettoyer les relations avant suppression"""
        # Supprimer les relations dans la vue avant de supprimer la catégorie
        for category in self:
            relations = self.env['product.compatibility.view'].search([('category_id', '=', category.id)])
            relations.unlink()
        
        return super().unlink()
    # Fin pour nouveau modele compatibilite product_compatibility_views


        
class ProductTemplate(models.Model):
    """Extension du modèle produit pour les catégories de compatibilité"""
    _inherit = 'product.template'

    # Catégories de compatibilité (nouveau champ Many2many)
    compatibility_category_ids = fields.Many2many(
        'compatibility.category',
        'product_compatibility_category_rel',
        'product_id', 'category_id',
        string=_('Compatibility category'),
        tracking=True,
        help=_("Compatibility categories for this product")
    )
    
    compatibility_category_count = fields.Integer(
        string=_("Compatibility category count"), 
        compute='_compute_compatibility_category_count'
    )

    compatibility_search_text = fields.Text(
        _('Compatibility search text'), 
        compute='_compute_compatibility_search_text', 
        store=True,
        index=True
    )


    @api.depends('compatibility_category_ids.complete_name')
    def _compute_compatibility_search_text(self):
        for record in self:
            # Concaténer tous les noms complets des catégories
            names = record.compatibility_category_ids.mapped('complete_name')
            record.compatibility_search_text = ' '.join(names)



    def _get_compatibility_categories_ordered(self):
        """Retourne les catégories de compatibilité triées"""
        return self.compatibility_category_ids.sorted('complete_name')

    @api.depends('compatibility_category_ids')
    def _compute_compatibility_category_count(self):
        for record in self:
            record.compatibility_category_count = len(record.compatibility_category_ids)

    def _add_parent_categories(self):
        """Ajouter automatiquement les catégories parentes"""
        categories_to_add = self.env['compatibility.category']
        
        # Pour chaque catégorie affectée, récupérer ses parents
        for category in self.compatibility_category_ids:
            # Récupérer tous les parents (sans la catégorie elle-même)
            parents = category.get_parent_categories(include_self=False)
            categories_to_add |= parents
        
        # Ajouter les catégories parentes manquantes
        missing_parents = categories_to_add - self.compatibility_category_ids
        if missing_parents:
            self.compatibility_category_ids = [(4, cat.id) for cat in missing_parents]

    def action_view_compatibility_categories(self):
        """Action pour voir/gérer les catégories de compatibilité"""
        action = {
            'type': 'ir.actions.act_window',
            'name': _('Compatibility category'),
            'res_model': 'compatibility.category',
            'view_mode': 'tree,form',
            'domain': [('product_ids', 'in', self.id)],
            'context': {
                'default_product_ids': [(6, 0, self.ids)],
            }
        }
        return action

    def remove_compatibility_category(self, category_id):
        """Retirer une catégorie de compatibilité"""
        if isinstance(category_id, int):
            category_id = [category_id]
            
        for cat_id in category_id:
            if cat_id in self.compatibility_category_ids.ids:
                self.compatibility_category_ids = [(3, cat_id)]
        return True

    @api.model
    def search_by_compatibility(self, category_ids=None, include_children=True):
        """Rechercher des produits par catégories de compatibilité"""
        if not category_ids:
            return self.browse()
        
        if include_children:
            # Inclure les catégories enfants pour trouver les produits
            CompatibilityCategory = self.env['compatibility.category']
            all_categories = CompatibilityCategory.search([
                ('id', 'child_of', category_ids)
            ])
            category_ids = all_categories.ids
        
        return self.search([
            ('compatibility_category_ids', 'in', category_ids)
        ])

    def get_products_in_category_tree(self, category_id):
        """Récupérer tous les produits d'une catégorie et ses enfants"""
        category = self.env['compatibility.category'].browse(category_id)
        all_categories = self.env['compatibility.category'].search([
            ('id', 'child_of', category.id)
        ])
        return self.search([
            ('compatibility_category_ids', 'in', all_categories.ids)
        ])

    def get_compatibility_paths(self):
        """Retourne les chemins complets des catégories de compatibilité"""
        paths = []
        for category in self.compatibility_category_ids:
            paths.append(category.complete_name)
        return paths

    def get_compatibility_tree(self):
        """Retourne la structure hiérarchique des compatibilités"""
        tree = {}
        for category in self.compatibility_category_ids:
            # Construire l'arbre hiérarchique
            current_level = tree
            path_parts = category.complete_name.split(' / ')
            
            for part in path_parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]
        
        return tree

    def has_compatibility_with(self, category_name):
        """Vérifier si le produit est compatible avec une catégorie"""
        return any(
            category_name.lower() in category.complete_name.lower() 
            for category in self.compatibility_category_ids
        )

    @api.model
    def get_products_by_compatibility_path(self, path_parts):
        """Récupérer les produits selon un chemin de compatibilité"""
        # Exemple: path_parts = ['FIAT', 'FULLBACK', '2016+']
        search_pattern = ' / '.join(path_parts)
        
        categories = self.env['compatibility.category'].search([
            ('complete_name', 'ilike', search_pattern)
        ])
        
        return categories.mapped('product_ids')


#    @api.model_create_multi
#    def create(self, vals_list):
#        """Override pour gérer l'affectation hiérarchique à la création"""
#        products = super().create(vals_list)
#        for product in products:
#            if product.compatibility_category_ids:
#                product._update_compatibility_hierarchy()
#        return products

#    def write(self, vals):
#        """Override pour gérer l'affectation hiérarchique à la modification"""
#        result = super().write(vals)
#        if 'compatibility_category_ids' in vals:
            # Traiter chaque produit individuellement
#            for product in self:
#                product._update_compatibility_hierarchy()
#        return result

#    def _update_compatibility_hierarchy(self):
#        """Méthode privée pour ajouter automatiquement les catégories parentes"""
        # Récupérer toutes les catégories actuellement affectées
#        current_categories = self.compatibility_category_ids
#        all_categories_to_add = self.env['compatibility.category']
        
        # Pour chaque catégorie affectée, récupérer tous ses parents
#        for category in current_categories:
#            parent_categories = category.get_parent_categories(include_self=True)
#            all_categories_to_add |= parent_categories
        
        # Mettre à jour les catégories seulement si nécessaire (éviter récursion)
#        missing_categories = all_categories_to_add - current_categories
#        if missing_categories:
            # Utiliser SQL direct pour éviter la récursion
#            for category in missing_categories:
#                self.env.cr.execute("""
#                    INSERT INTO product_compatibility_category_rel (product_id, category_id)
#                    VALUES (%s, %s)
#                    ON CONFLICT DO NOTHING
#                """, (self.id, category.id))
            
            # Invalider le cache pour ce champ
#            self.invalidate_recordset(['compatibility_category_ids'])



#    def write(self, vals):
#        """Recalculer les champs des variants quand les compatibilités changent"""
#        result = super().write(vals)
        
#        if 'compatibility_category_ids' in vals:
            # Recalculer pour tous les variants
#            variants = self.mapped('product_variant_ids')
#            if variants:
#                variants._compute_compatibility_categories()
#                variants._compute_compatibility_search_text()
        
#        return result


    # Nouveau 02.08.25 pour nouveau modele compatibilite product_compatibility_views
    @api.model_create_multi
    def create(self, vals_list):
        """Override create pour synchroniser automatiquement les nouvelles relations"""
        products = super().create(vals_list)
        
        # Synchroniser les produits qui ont des catégories de compatibilité
        for product in products:
            if product.compatibility_category_ids:
                self.env['product.compatibility.view'].sync_product_relations(product.id)
        
        return products

    def write(self, vals):
        """Override write pour synchroniser quand les compatibilités changent"""
        result = super().write(vals)
        
        # Si les catégories de compatibilité ont changé, resynchroniser dans le product template et variant
        if 'compatibility_category_ids' in vals:
            for product in self:
                self.env['product.compatibility.view'].sync_product_relations(product.id)
                
                # Ajout 11.08.25 Forcer le recalcul sur les variantes
                #product.product_variant_ids._compute_compatibility_category_panel_id()
                #product.product_variant_ids._compute_compatibility_category_panel_normalized()
        return result

    def unlink(self):
        """Override unlink pour nettoyer les relations avant suppression"""
        # Supprimer les relations dans la vue avant de supprimer le produit
        for product in self:
            relations = self.env['product.compatibility.view'].search([('product_id', '=', product.id)])
            relations.unlink()
        
        return super().unlink()
    # Fin pour nouveau modele compatibilite product_compatibility_views


class VehicleBrand(models.Model):
    _name = 'vehicle.brands'
    _description = 'Vehicle Brand'

    name = fields.Char("Brand", required=True)
    model_ids = fields.One2many('vehicle.models', 'brand_id', string="Models")

    # ✅ RELATIONS DIRECTES POUR L'EXPORT
    year_ids = fields.One2many('vehicle.years', 'brand_id', string="Years")
    series_ids = fields.One2many('vehicle.serieses', 'brand_id', string="Series")
    variant_ids = fields.One2many('vehicle.variants', 'brand_id', string="Variants")



class VehicleModel(models.Model):
    _name = 'vehicle.models'
    _description = 'Vehicle Model'

    name = fields.Char("Model", required=True)
    brand_id = fields.Many2one('vehicle.brands', string="Brand", required=True, ondelete='cascade')
    year_ids = fields.One2many('vehicle.years', 'model_id', string="Years")


class VehicleYear(models.Model):
    _name = 'vehicle.years'
    _description = 'Vehicle Year'

    name = fields.Char("Year", required=True)
    model_id = fields.Many2one('vehicle.models', string="Model", required=True, ondelete='cascade')
    series_ids = fields.One2many('vehicle.serieses', 'year_id', string="Series")

    # ✅ NOUVEAU - Pour l'export
    brand_id = fields.Many2one(
        'vehicle.brands', 
        string="Brand", 
        related='model_id.brand_id',
        store=True,
        index=True
    )

class VehicleSeries(models.Model):
    _name = 'vehicle.serieses'
    _description = 'Vehicle Series'

    name = fields.Char("Series", required=True)
    year_id = fields.Many2one('vehicle.years', string="Year", required=True, ondelete='cascade')
    variant_ids = fields.One2many('vehicle.variants', 'series_id', string="Variants")

    # ✅ NOUVEAU - Pour l'export
    brand_id = fields.Many2one(
        'vehicle.brands', 
        string="Brand", 
        related='year_id.model_id.brand_id',
        store=True,
        index=True
    )

    model_id = fields.Many2one(
        'vehicle.models', 
        string="Model", 
        related='year_id.model_id',
        store=True,
        index=True
    )

class VehicleVariant(models.Model):
    _name = 'vehicle.variants'
    _description = 'Vehicle Variant'

    name = fields.Char("Variant", required=True)
    series_id = fields.Many2one('vehicle.serieses', string="Series", required=True, ondelete='cascade')

    # ✅ NOUVEAU - Pour l'export
    brand_id = fields.Many2one(
        'vehicle.brands', 
        string="Brand", 
        related='series_id.year_id.model_id.brand_id',
        store=True,
        index=True
    )
    model_id = fields.Many2one(
        'vehicle.models', 
        string="Model", 
        related='series_id.year_id.model_id',
        store=True,
        index=True
    )
    year_id = fields.Many2one(
        'vehicle.years', 
        string="Year", 
        related='series_id.year_id',
        store=True,
        index=True
    )