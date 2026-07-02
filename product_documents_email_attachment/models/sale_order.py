# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_product_documents_attachments(self):
        """Récupère les IDs des attachments des documents produits cochés"""
        attachment_ids = []
        url_documents = []  # Pour tracker les documents URL
        seen_products = set()
        
        for line in self.order_line:
            product_id = line.product_id.id
            
            # Éviter les doublons pour le même produit
            if product_id not in seen_products:
                seen_products.add(product_id)
                
                # Chercher les product.document du produit qui sont cochés
                product_docs = self.env['product.document'].search([
                    ('res_model', '=', 'product.product'),
                    ('res_id', '=', product_id),
                    ('include_in_email', '=', True)
                ])
                
                # Ajouter aussi ceux du template produit
                template_docs = self.env['product.document'].search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', line.product_id.product_tmpl_id.id),
                    ('include_in_email', '=', True)
                ])
                
                # Récupérer les ir_attachment_id de ces documents
                all_docs = product_docs + template_docs
                for doc in all_docs:
                    if doc.ir_attachment_id:
                        # Vérifier si c'est un fichier physique ou une URL (Ajout 31.12.2025)
                        attachment = doc.ir_attachment_id
                        if attachment.type == 'url':
                            # C'est une URL, on la garde séparément
                            url_documents.append({
                                'name': attachment.name,
                                'url': attachment.url,
                            })
                        else:
                            # C'est un fichier physique
                            attachment_ids.append(attachment.id)
        
        return attachment_ids, url_documents

#                        attachment_ids.append(doc.ir_attachment_id.id)
        
#        return attachment_ids


    def _get_optional_product_documents_attachments(self):
        """Récupère les IDs des attachments des documents des produits optionnels cochés"""
        attachment_ids = []
        url_documents = []
        seen_products = set()
        
        # Parcourir les lignes optionnelles
        for line in self.sale_order_option_ids:
            product_id = line.product_id.id
            
            # Éviter les doublons pour le même produit
            if product_id not in seen_products:
                seen_products.add(product_id)
                
                # Chercher les product.document du produit qui sont cochés
                product_docs = self.env['product.document'].search([
                    ('res_model', '=', 'product.product'),
                    ('res_id', '=', product_id),
                    ('include_in_email', '=', True)
                ])
                
                # Ajouter aussi ceux du template produit
                template_docs = self.env['product.document'].search([
                    ('res_model', '=', 'product.template'),
                    ('res_id', '=', line.product_id.product_tmpl_id.id),
                    ('include_in_email', '=', True)
                ])
                
                # Récupérer les ir_attachment_id de ces documents
                all_docs = product_docs + template_docs
                for doc in all_docs:
                    if doc.ir_attachment_id:
                        attachment = doc.ir_attachment_id
                        if attachment.type == 'url':
                            url_documents.append({
                                'name': attachment.name,
                                'url': attachment.url,
                            })
                        else:
                            attachment_ids.append(attachment.id)
        
        return attachment_ids, url_documents


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_add_product_documents(self):
        """Ajouter directement les documents produits cochés aux pièces jointes"""
        
        # Vérifier que c'est bien un email de devis
        if self.model != 'sale.order' or not self.res_ids:
            raise UserError(_("This action is only available for quotes."))
        
        # Récupérer le devis
        sale_order_id = self._get_sale_order_id()
        sale_order = self.env['sale.order'].browse(sale_order_id)
        
        if not sale_order.exists():
            raise UserError(_("Quote not found."))
        
        # Récupérer les documents produits cochés
#        product_attachment_ids = sale_order._get_product_documents_attachments()
        product_attachment_ids, url_documents = sale_order._get_product_documents_attachments()
        
#        if not product_attachment_ids:
        if not product_attachment_ids and not url_documents:
            raise UserError(
                _("No documents selected.\n\n"
                "To add documents:\n"
                "1. Go to the Documents tab for your products\n"
                "2. Check the ‘Attach to email’ box on the desired documents\n"
                "3. Come back here and click this button again")
            )
        
        # Récupérer les attachments actuels
        current_attachment_ids = self.attachment_ids.ids
        
        # Ajouter les nouveaux documents (éviter les doublons)
        new_attachment_ids = []
        for att_id in product_attachment_ids:
            if att_id not in current_attachment_ids:
                new_attachment_ids.append(att_id)
        
#        if new_attachment_ids:
            # Ajouter les nouveaux documents aux pièces jointes
#            self.write({'attachment_ids': [(4, att_id) for att_id in new_attachment_ids]})
            
            # Forcer le rafraîchissement en relisant l'enregistrement
#            self = self.browse(self.id)
            
            # Récupérer les noms des documents ajoutés pour le message
#            added_attachments = self.env['ir.attachment'].browse(new_attachment_ids)
#            doc_names = [att.name for att in added_attachments]
            
            # Message de confirmation simple
#            message = _("✅ %d document(s) successfully added !") % len(new_attachment_ids)
            
            # Retourner une action pour recharger complètement la vue
#            return {
#                'type': 'ir.actions.act_window',
#                'res_model': 'mail.compose.message',
#                'res_id': self.id,
#                'view_mode': 'form',
#                'target': 'new',
#                'context': dict(self.env.context)
#            }
#        else:
#            raise UserError(_("All documents produced are already attached to this email."))

        # AJOUT: Gérer les fichiers et URLs
        if new_attachment_ids or url_documents:
            # Ajouter les fichiers aux pièces jointes
            if new_attachment_ids:
                self.write({'attachment_ids': [(4, att_id) for att_id in new_attachment_ids]})
            
            # AJOUT: Ajouter les URLs dans le corps du mail
            if url_documents:
                # Utiliser la méthode Odoo pour ajouter du contenu HTML
                from markupsafe import Markup
                
                url_html = Markup("""
                    <br/>
                    <div style="background-color: #e8f4f8; border: 1px solid #b8dce8; border-radius: 4px; padding: 15px; margin: 15px 0;">
                        <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #31708f;">
                            📎 Documents
                        </p>
                        <ul style="margin: 0; padding-left: 20px; list-style-type: disc;">
                """)
                
                for url_doc in url_documents:
                    url_html += Markup(f"""
                        <li style="margin: 8px 0;">
                            <a href="{url_doc['url']}" target="_blank" style="color: #337ab7; text-decoration: underline; font-size: 14px;">
                                {url_doc['name']}
                            </a>
                        </li>
                    """)
                
                url_html += Markup("</ul></div>")
                
                # Récupérer le corps actuel
                current_body = self.body or Markup('<p><br/></p>')
                
                # Combiner
                new_body = Markup(str(current_body) + str(url_html))
                
                self.write({'body': new_body})
            
            # Forcer le rafraîchissement en relisant l'enregistrement
            self = self.browse(self.id)
            
            # MODIFIÉ: Message de confirmation adapté
            message_parts = []
            if new_attachment_ids:
                message_parts.append(_("%d file(s)") % len(new_attachment_ids))
            if url_documents:
                message_parts.append(_("%d link(s)") % len(url_documents))
            
            message = _("✅ %s successfully added!") % _(" and ").join(message_parts)
            
            # Retourner une action pour recharger complètement la vue
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                'context': dict(self.env.context)
            }
        else:
            raise UserError(_("All documents produced are already attached to this email."))


    def action_add_optional_product_documents(self):
        """Ajouter les documents des produits optionnels cochés aux pièces jointes"""
        
        # Vérifier que c'est bien un email de devis
        if self.model != 'sale.order' or not self.res_ids:
            raise UserError(_("This action is only available for quotes."))
        
        # Récupérer le devis
        sale_order_id = self._get_sale_order_id()
        sale_order = self.env['sale.order'].browse(sale_order_id)
        
        if not sale_order.exists():
            raise UserError(_("Quote not found."))
        
        # Récupérer les documents des produits optionnels cochés
        product_attachment_ids, url_documents = sale_order._get_optional_product_documents_attachments()
        
        if not product_attachment_ids and not url_documents:
            raise UserError(
                _("No optional product documents selected.\n\n"
                "To add documents:\n"
                "1. Go to the Documents tab for your optional products\n"
                "2. Check the 'Attach to email' box on the desired documents\n"
                "3. Come back here and click this button again")
            )
        
        # Récupérer les attachments actuels
        current_attachment_ids = self.attachment_ids.ids
        
        # Ajouter les nouveaux documents (éviter les doublons)
        new_attachment_ids = []
        for att_id in product_attachment_ids:
            if att_id not in current_attachment_ids:
                new_attachment_ids.append(att_id)
        
        # Gérer les fichiers et URLs
        if new_attachment_ids or url_documents:
            # Ajouter les fichiers aux pièces jointes
            if new_attachment_ids:
                self.write({'attachment_ids': [(4, att_id) for att_id in new_attachment_ids]})
            
            # Ajouter les URLs dans le corps du mail
            if url_documents:
                from markupsafe import Markup
                
                url_html = Markup("""
                    <br/>
                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 4px; padding: 15px; margin: 15px 0;">
                        <p style="margin: 0 0 10px 0; font-size: 14px; font-weight: bold; color: #856404;">
                            📋 Option Documents
                        </p>
                        <ul style="margin: 0; padding-left: 20px; list-style-type: disc;">
                """)
                
                for url_doc in url_documents:
                    url_html += Markup(f"""
                        <li style="margin: 8px 0;">
                            <a href="{url_doc['url']}" target="_blank" style="color: #337ab7; text-decoration: underline; font-size: 14px;">
                                {url_doc['name']}
                            </a>
                        </li>
                    """)
                
                url_html += Markup("</ul></div>")
                
                # Récupérer le corps actuel
                current_body = self.body or Markup('<p><br/></p>')
                
                # Combiner
                new_body = Markup(str(current_body) + str(url_html))
                
                self.write({'body': new_body})
            
            # Forcer le rafraîchissement
            self = self.browse(self.id)
            
            # Message de confirmation adapté
            message_parts = []
            if new_attachment_ids:
                message_parts.append(_("%d optional file(s)") % len(new_attachment_ids))
            if url_documents:
                message_parts.append(_("%d optional link(s)") % len(url_documents))
            
            message = _("✅ %s successfully added!") % _(" and ").join(message_parts)
            
            # Retourner une action pour recharger complètement la vue
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'mail.compose.message',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                'context': dict(self.env.context)
            }
        else:
            raise UserError(_("All optional product documents are already attached to this email."))


    def _get_sale_order_id(self):
        """Récupérer l'ID du devis de manière sécurisée"""
        try:
            if isinstance(self.res_ids, str):
                import ast
                res_ids = ast.literal_eval(self.res_ids)
            else:
                res_ids = self.res_ids
            
            return res_ids[0] if isinstance(res_ids[0], int) else int(res_ids[0])
            
        except (ValueError, TypeError, IndexError, SyntaxError):
            raise UserError(_("Error retrieving quote."))