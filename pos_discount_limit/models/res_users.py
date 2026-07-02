from odoo import fields, models, _

class ResUsers(models.Model):
    _inherit = 'res.users'
    
    limited_discount = fields.Integer(string=_("POS Discount Limit"),
                                      help=_("Provide discount limit to each "
                                           "employee"))