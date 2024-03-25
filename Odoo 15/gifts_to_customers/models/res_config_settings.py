# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    product_gift = fields.Many2one(string="Producto de regalo", related='company_id.product_gift', readonly=False,)
    this_company_give_gift = fields.Boolean(string="Esta compañía da regalos", related='company_id.this_company_give_gift', readonly=False,)