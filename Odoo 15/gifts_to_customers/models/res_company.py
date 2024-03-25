# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    product_gift = fields.Many2one('product.template', string="Producto de regalo", domain=[('is_gift', '=', True)])
    this_company_give_gift = fields.Boolean(string="Esta compañía da regalos", default=False)