# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _get_quotation_origin(self):
        for stock_row in self:
            quotation_origin = ''
            if stock_row.sale_id:
                if stock_row.sale_id.quotation_origin:
                    quotation_origin = stock_row.sale_id.quotation_origin
            elif stock_row.purchase_id:
                if stock_row.purchase_id.quotation_origin:
                    quotation_origin = stock_row.purchase_id.quotation_origin
            stock_row.quotation_origin = quotation_origin
        return {}
    
    quotation_origin = fields.Char('Cotización Origen', copy=False, compute="_get_quotation_origin")