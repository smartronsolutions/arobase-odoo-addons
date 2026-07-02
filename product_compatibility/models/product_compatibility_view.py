# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductCompatibilityView(models.Model):
    """
    Modèle intermédiaire : une ligne par relation produit-catégorie
    Résout le problème de filtrage en séparant physiquement chaque relation
    """
    _name = 'product.compatibility.view'
    _description = 'Vue produit-compatibilité (une relation par enregistrement)'
    _order = 'product_name, category_name'
    _rec_name = 'display_name'

    # Relations de base (cœur du modèle)
    product_id = fields.Many2one(
        'product.template', 
        string=_('Product'),
        required=True,
        ondelete='cascade',
        index=True
    )
    
    category_id = fields.Many2one(
        'compatibility.category',
        string=_('Compatibility category'), 
        required=True,
        ondelete='cascade',
        index=True
    )

    # Champs dénormalisés du produit (pour performance et affichage)
    product_name = fields.Char(
        string=_('Product name'),
        related='product_id.name', 
        store=True,
        index=True
    )
    
    default_code = fields.Char(
        string=_('Default code'),
        related='product_id.default_code', 
        store=True,
        index=True
    )
    
    list_price = fields.Float(
        string=_('Price'),
        related='product_id.list_price', 
        store=True
    )
    
    standard_price = fields.Float(
        string=_('Cost'),
        related='product_id.standard_price', 
        store=True
    )
    
    qty_available = fields.Float(
        string=_('Qty available'),
        related='product_id.qty_available', 
        store=False  # Pas stocké car change souvent
    )
    
    categ_id = fields.Many2one(
        'product.category',
        string=_('Product category'),
        related='product_id.categ_id',
        store=True
    )
    
    active = fields.Boolean(
        string=_('Active'),
        related='product_id.active',
        store=True
    )

    # Champs dénormalisés de la catégorie (pour recherche optimisée)
    category_name = fields.Char(
        string=_('Category name'),
        related='category_id.name', 
        store=True,
        index=True
    )
    
    category_complete_name = fields.Char(
        string=_('Category complete name'),
        related='category_id.complete_name', 
        store=True,
        index=True
    )
    
    category_parent_id = fields.Many2one(
        'compatibility.category',
        string=_('Parent category'),
        related='category_id.parent_id',
        store=True
    )

    # Champ d'affichage principal
    display_name = fields.Char(
        string=_('Display name'),
        compute='_compute_display_name',
        store=True
    )
    
    # Champ de recherche optimisé
    search_text = fields.Text(
        string=_('Search text'),
        compute='_compute_search_text',
        store=True,
        index=True
    )

    # Contrainte d'unicité
    _sql_constraints = [
        ('unique_product_category', 
         'UNIQUE(product_id, category_id)', 
         _('A product-category relationship can only exist once.'))
    ]

    @api.depends('product_name', 'category_complete_name')
    def _compute_display_name(self):
        """Calcule le nom d'affichage de la relation"""
        for record in self:
            record.display_name = f"{record.product_name} → {record.category_complete_name}"

    @api.depends('product_name', 'default_code', 'category_name', 'category_complete_name')
    def _compute_search_text(self):
        """Calcule le texte de recherche optimisé"""
        for record in self:
            search_parts = [
                record.product_name or '',
                record.default_code or '',
                record.category_name or '',
                record.category_complete_name or ''
            ]
            record.search_text = ' '.join(filter(None, search_parts)).lower()

    def name_get(self):
        """Affichage personnalisé dans les listes déroulantes"""
        result = []
        for record in self:
            name = f"{record.product_name} ({record.category_name})"
            result.append((record.id, name))
        return result

    @api.model
    def search_by_compatibility(self, search_term, limit=None, offset=0):
        """
        Recherche optimisée par compatibilité - résout le problème de filtrage
        
        Args:
            search_term (str): Terme de recherche
            limit (int): Limite de résultats
            offset (int): Décalage pour pagination
            
        Returns:
            recordset: Relations produit-catégorie filtrées
        """
        domain = [('active', '=', True)]
        
        if search_term:
            search_term = search_term.strip()
            domain.extend([
                '|', '|', '|',
                ('category_name', 'ilike', search_term),
                ('category_complete_name', 'ilike', search_term),
                ('product_name', 'ilike', search_term),
                ('default_code', 'ilike', search_term)
            ])
        
        return self.search(domain, limit=limit, offset=offset, order=self._order)

    def action_view_product(self):
        """Action pour voir le produit"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Product'),
            'res_model': 'product.template',
            'res_id': self.product_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_category(self):
        """Action pour voir la catégorie de compatibilité"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compatibility category'),
            'res_model': 'compatibility.category',
            'res_id': self.category_id.id,
            'view_mode': 'form',
            'target': 'current',
        }



    @api.model
    def sync_all_products(self):
        """
        Synchronisation initiale : crée toutes les relations pour tous les produits existants
        À utiliser lors de l'installation du nouveau modèle
        """
        # Vider la table avant de recréer
        self.search([]).unlink()
        
        # Récupérer tous les produits avec des compatibilités
        products_with_compatibility = self.env['product.template'].search([
            ('compatibility_category_ids', '!=', False),
            ('active', '=', True)
        ])
        
        relations_to_create = []
        for product in products_with_compatibility:
            for category in product.compatibility_category_ids:
                relations_to_create.append({
                    'product_id': product.id,
                    'category_id': category.id
                })
        
        # Création en lot pour les performances
        if relations_to_create:
            self.create(relations_to_create)
        
        return len(relations_to_create)

    @api.model
    def sync_product_relations(self, product_id):
        """
        Synchronise les relations pour un produit spécifique
        
        Args:
            product_id (int): ID du produit à synchroniser
        """
        # Supprimer les anciennes relations de ce produit
        old_relations = self.search([('product_id', '=', product_id)])
        old_relations.unlink()
        
        # Récupérer le produit et ses catégories actuelles
        product = self.env['product.template'].browse(product_id)
        if not product.exists() or not product.active:
            return
        
        # Créer les nouvelles relations
        new_relations = []
        for category in product.compatibility_category_ids:
            new_relations.append({
                'product_id': product.id,
                'category_id': category.id
            })
        
        if new_relations:
            self.create(new_relations)


    # Ajout 11.08.25 Champ de recherche normalisé (sans les /)
    category_search_normalized = fields.Char(
        string=_('Category search normalized'),
        compute='_compute_category_search_normalized',
        store=True,
        index=True
    )

    @api.depends('category_complete_name')
    def _compute_category_search_normalized(self):
        """Crée un champ de recherche sans les séparateurs"""
        for record in self:
            if record.category_complete_name:
                # Remplacer " / " par " " et mettre en minuscules
                normalized = record.category_complete_name.replace(' / ', ' ').lower()
                record.category_search_normalized = normalized
            else:
                record.category_search_normalized = ''


