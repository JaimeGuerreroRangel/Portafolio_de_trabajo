# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'
    
    company_id = fields.Many2one('res.company', string='Compañía', index=True, default=lambda self: self.env.company)
     