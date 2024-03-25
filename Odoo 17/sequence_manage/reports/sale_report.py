# -*- encoding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.addons.sale.models.sale_order import SALE_ORDER_STATE

class SaleReport(models.Model):
    _inherit = "sale.report"
    
    quotation_origin = fields.Char(string="Cotización Origen", readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['quotation_origin'] = "s.quotation_origin"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += """,
            s.quotation_origin"""
        return res