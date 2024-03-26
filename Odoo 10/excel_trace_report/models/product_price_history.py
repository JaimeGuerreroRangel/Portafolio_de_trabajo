# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from pytz import timezone

class ProductPriceHistory(models.Model):
    _inherit = 'product.price.history'

    user_id = fields.Many2one('res.users', 'Usuario', default=lambda self: self.env.user, store=True)

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _set_standard_price(self, value):
        PriceHistory = self.env['product.price.history']
        for product in self:
            PriceHistory.create({
                'product_id': product.id,
                'cost': value,
                'company_id': self._context.get('force_company', self.env.user.company_id.id),
                'user_id': self.env.uid,
            })
        