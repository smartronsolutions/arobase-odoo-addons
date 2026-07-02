from odoo import models, fields

class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    detailed_accounting_entries = fields.Boolean(
        string='Écritures comptables détaillées',
        default=False,
        help="Si activé, génère une écriture comptable pour chaque paiement "
             "au lieu de les consolider par méthode de paiement"
    )

    auto_reconcile_receivables = fields.Boolean(
        string="Lettrage automatique",
        default=True,    
        help="Lettrer automatiquement les comptes clients POS lors de la fermeture de session"
    )