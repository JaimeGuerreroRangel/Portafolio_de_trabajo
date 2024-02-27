# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_gift = fields.Boolean(string="Es regalo", default=False)
    give_gift = fields.Boolean(string="Da regalo", default=False)
    