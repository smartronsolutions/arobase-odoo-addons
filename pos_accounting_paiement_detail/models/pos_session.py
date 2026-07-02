from odoo import models, fields, api, _
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    def _create_bank_payment_moves(self, data):
        """
        Override pour créer des écritures détaillées de paiements bancaires
        """
        if not self.config_id.detailed_accounting_entries:
            # Comportement standard
            return super()._create_bank_payment_moves(data)
        
#        self.message_post(body="🏦 CRÉATION PAIEMENTS BANCAIRES DÉTAILLÉS")
        
        # Récupérer les paiements bancaires combinés et les diviser
        combine_receivables_bank = data.get('combine_receivables_bank', {})
        split_receivables_bank = data.get('split_receivables_bank', {})
        MoveLine = data.get('MoveLine')
        
        payment_method_to_receivable_lines = {}
        payment_to_receivable_lines = {}
        
        # Pour chaque méthode de paiement bancaire, créer des paiements individuels
        for payment_method, amounts in combine_receivables_bank.items():
            individual_payments = self._get_individual_bank_payments(payment_method)
            
            for payment_obj in individual_payments:
                # Construire la référence avec numéro de chèque si applicable
                reference = self._build_payment_reference(payment_obj)
                
                # Créer une ligne receivable pour ce paiement spécifique
                receivable_vals = {
                    'name': reference,
                    'account_id': self.company_id.account_default_pos_receivable_account_id.id,
                    'move_id': self.move_id.id,
                    'partner_id': False,
                }
                
                # Utiliser les méthodes standard pour le débit/crédit
                receivable_vals = self._debit_amounts(
                    receivable_vals, 
                    payment_obj.amount, 
                    payment_obj.amount
                )
                receivable_line = MoveLine.create(receivable_vals)
                
                # Créer le paiement account.payment correspondant avec la même référence
                payment_receivable_line = self._create_individual_account_payment(payment_obj, reference)
                
                # Stocker pour réconciliation
                payment_to_receivable_lines[payment_obj] = receivable_line | payment_receivable_line
                
#                self.message_post(body=f"💳 Paiement bancaire détaillé créé: {reference}")
        
        # Vider les paiements combinés puisqu'on les a traités individuellement
        data['combine_receivables_bank'] = {}
        
        # Traiter les paiements split restants avec la méthode standard
        result = super()._create_bank_payment_moves(data)
        
        # Ajouter nos nouvelles lignes aux données de retour
        if 'payment_to_receivable_lines' not in data:
            data['payment_to_receivable_lines'] = {}
        data['payment_to_receivable_lines'].update(payment_to_receivable_lines)
        
#        self.message_post(body="✅ Paiements bancaires détaillés créés")
        return data
    
    def _create_cash_statement_lines_and_cash_move_lines(self, data):
        """
        Override pour créer des lignes de caisse détaillées
        """
        if not self.config_id.detailed_accounting_entries:
            # Comportement standard
            return super()._create_cash_statement_lines_and_cash_move_lines(data)
        
#        self.message_post(body="💰 CRÉATION LIGNES CAISSE DÉTAILLÉES")
        
        # Récupérer les paiements cash combinés et les diviser
        combine_receivables_cash = data.get('combine_receivables_cash', {})
        split_receivables_cash = data.get('split_receivables_cash', {})
        MoveLine = data.get('MoveLine')
        BankStatementLine = self.env['account.bank.statement.line']
        
        split_cash_statement_lines = []
        split_cash_receivable_lines = []
        
        # Pour chaque méthode de paiement cash, créer des lignes individuelles
        for payment_method, amounts in combine_receivables_cash.items():
            individual_payments = self._get_individual_cash_payments(payment_method)
            
            for payment_obj in individual_payments:
                # Construire la référence avec numéro de chèque si applicable
                reference = self._build_payment_reference(payment_obj)
                
                # Créer la ligne de relevé bancaire pour ce paiement
                statement_line_vals = {
                    'date': fields.Date.context_today(self, timestamp=payment_obj.payment_date),
                    'amount': payment_obj.amount,
                    'payment_ref': reference,
                    'pos_session_id': self.id,
                    'journal_id': payment_method.journal_id.id,
                    'counterpart_account_id': self.company_id.account_default_pos_receivable_account_id.id,
                }
                statement_line = BankStatementLine.create(statement_line_vals)
                split_cash_statement_lines.append(statement_line)
                
                # Créer la ligne receivable correspondante dans l'écriture principale
                receivable_vals = {
                    'name': reference,
                    'account_id': self.company_id.account_default_pos_receivable_account_id.id,
                    'move_id': self.move_id.id,
                    'partner_id': False,
                }
                receivable_vals = self._debit_amounts(
                    receivable_vals, 
                    payment_obj.amount, 
                    payment_obj.amount
                )
                receivable_line = MoveLine.create(receivable_vals)
                split_cash_receivable_lines.append(receivable_line)
                
#                self.message_post(body=f"💰 Ligne caisse détaillée créée: {reference}")
        
        # Vider les paiements combinés puisqu'on les a traités individuellement
        data['combine_receivables_cash'] = {}
        
        # Traiter les paiements split restants avec la méthode standard
        result = super()._create_cash_statement_lines_and_cash_move_lines(data)
        
        # Ajouter nos nouvelles lignes aux données de retour
        statement_lines_from_moves = []
        for stmt_line in split_cash_statement_lines:
            statement_lines_from_moves.extend(
                stmt_line.move_id.line_ids.filtered(
                    lambda line: line.account_id.account_type == 'asset_receivable'
                )
            )
        
        if 'split_cash_statement_lines' not in data:
            data['split_cash_statement_lines'] = self.env['account.move.line']
        if 'split_cash_receivable_lines' not in data:
            data['split_cash_receivable_lines'] = self.env['account.move.line']
            
        data['split_cash_statement_lines'] = data['split_cash_statement_lines'] | self.env['account.move.line'].browse([l.id for l in statement_lines_from_moves])
        data['split_cash_receivable_lines'] = data['split_cash_receivable_lines'] | self.env['account.move.line'].browse([l.id for l in split_cash_receivable_lines])
        
#        self.message_post(body="✅ Lignes caisse détaillées créées")
        return data
    
    def _get_individual_bank_payments(self, payment_method):
        """
        Récupère tous les paiements bancaires individuels pour une méthode donnée
        """
        payments = []
        closed_orders = self._get_closed_orders()
        
        for order in closed_orders:
            for payment_line in order.payment_ids:
                if (payment_line.payment_method_id == payment_method and 
                    payment_method.type == 'bank'):
                    payments.append(payment_line)
        
        return payments
    
    def _get_individual_cash_payments(self, payment_method):
        """
        Récupère tous les paiements cash individuels pour une méthode donnée
        """
        payments = []
        closed_orders = self._get_closed_orders()
        
        for order in closed_orders:
            for payment_line in order.payment_ids:
                if (payment_line.payment_method_id == payment_method and 
                    payment_method.type == 'cash'):
                    payments.append(payment_line)
        
        return payments
    
    def _create_individual_account_payment(self, payment_obj, reference=None):
        """
        Crée un account.payment individuel pour un paiement POS
        """
        payment_method = payment_obj.payment_method_id
        amount = payment_obj.amount
        
        outstanding_account = (payment_method.outstanding_account_id or 
                             self.company_id.account_journal_payment_debit_account_id)
        destination_account = self.company_id.account_default_pos_receivable_account_id
        
        if amount < 0:
            # Inverser les comptes pour les montants négatifs
            outstanding_account, destination_account = destination_account, outstanding_account
        
        # Utiliser la référence fournie ou en construire une
        if not reference:
            reference = self._build_payment_reference(payment_obj)
        
        account_payment = self.env['account.payment'].create({
            'amount': abs(amount),
            'journal_id': payment_method.journal_id.id,
            'force_outstanding_account_id': outstanding_account.id,
            'destination_account_id': destination_account.id,
            'ref': reference,
            'pos_payment_method_id': payment_method.id,
            'pos_session_id': self.id,
            'company_id': self.company_id.id,
        })
        
        account_payment.action_post()
        return account_payment.move_id.line_ids.filtered(
            lambda line: line.account_id == account_payment.destination_account_id
        )
    
    def _build_payment_reference(self, payment_obj):
        """
        Construit la référence du paiement avec numéro de chèque si applicable
        """
        payment_method = payment_obj.payment_method_id
        order_name = payment_obj.pos_order_id.name
        session_name = payment_obj.session_id.name
        
        # Base de la référence
        reference_parts = [payment_method.name]
        
        # Ajouter le numéro de chèque s'il existe
#        if hasattr(payment_obj, 'check_number') and payment_obj.check_number:
#            reference_parts.append(f"N°{payment_obj.check_number}")

        # Ajouter le numéro de chèque s'il existe (module bi_pos_check_info optionnel)
        try:
            if hasattr(payment_obj, 'check_number') and payment_obj.check_number:
                reference_parts.append(f"N°{payment_obj.check_number}")
        except Exception:
            # Le module bi_pos_check_info n'est pas installé ou le champ n'existe pas
            pass

        # Ajouter le nom de la commande et le nom de la session
        reference_parts.extend([order_name, session_name])
        
        return " - ".join(reference_parts)
    
    def _reconcile_account_move_lines(self, data):
        """
        Override pour ajouter le lettrage automatique des comptes tiers si activé
        """
        # Appeler d'abord la méthode standard
        result = super()._reconcile_account_move_lines(data)
        
        # Si écritures détaillées activées et lettrage automatique souhaité
        if (self.config_id.detailed_accounting_entries and 
            hasattr(self.config_id, 'auto_reconcile_receivables') and 
            self.config_id.auto_reconcile_receivables):
            
            self._auto_reconcile_pos_receivables(data)
        
        return result
    
    def _auto_reconcile_pos_receivables(self, data):
        """
        Effectue le lettrage automatique de tous les comptes clients POS de la session
        """
        try:
#            self.message_post(body="🔄 DÉBUT LETTRAGE AUTOMATIQUE")
            
            # Récupérer toutes les lignes du compte client POS de cette session
            pos_receivable_account = self.company_id.account_default_pos_receivable_account_id
            
            # Lignes de l'écriture principale
            main_move_lines = self.move_id.line_ids.filtered(
                lambda l: l.account_id == pos_receivable_account and not l.reconciled
            )
            
            # Lignes des paiements (account.payment)
            payment_lines = self.env['account.move.line']
            
            # Récupérer les lignes des paiements bancaires
            payment_to_receivable_lines = data.get('payment_to_receivable_lines', {})
            for payment_obj, lines in payment_to_receivable_lines.items():
                payment_lines |= lines.filtered(
                    lambda l: l.account_id == pos_receivable_account and not l.reconciled
                )
            
            # Récupérer les lignes des paiements cash (relevés bancaires)
            split_cash_statement_lines = data.get('split_cash_statement_lines', self.env['account.move.line'])
            for line in split_cash_statement_lines:
                if line.account_id == pos_receivable_account and not line.reconciled:
                    payment_lines |= line
            
            # Regrouper par montant pour le lettrage
            all_lines = main_move_lines | payment_lines
            lines_by_amount = {}
            
            for line in all_lines:
                amount_key = abs(line.balance)
                if amount_key not in lines_by_amount:
                    lines_by_amount[amount_key] = []
                lines_by_amount[amount_key].append(line)
            
            # Effectuer le lettrage pour chaque groupe de montant
            reconciled_count = 0
            for amount, lines in lines_by_amount.items():
                if len(lines) >= 2:
                    # Vérifier que la somme des balances = 0
                    total_balance = sum(line.balance for line in lines)
                    if abs(total_balance) < 0.01:  # Tolérance pour les arrondis
                        try:
                            self.env['account.move.line'].browse([l.id for l in lines]).with_context(no_cash_basis=True).reconcile()
                            reconciled_count += len(lines)
#                            self.message_post(body=f"✅ Lettrage réussi pour {len(lines)} lignes de {amount}€")
                        except Exception as e:
                            self.message_post(body=f"⚠️ Échec lettrage pour montant {amount}€: {str(e)}")
            
#            self.message_post(body=f"🔄 LETTRAGE TERMINÉ: {reconciled_count} lignes lettrées")
            
        except Exception as e:
            error_msg = f"❌ ERREUR lettrage automatique: {str(e)}"
            _logger.error(error_msg, exc_info=True)
            self.message_post(body=error_msg)