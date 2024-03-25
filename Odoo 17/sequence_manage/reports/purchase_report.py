# -*- encoding: utf-8 -*-

from odoo import fields, models, api

class PurchaseReport(models.Model):
    _inherit = "purchase.report"
    
    quotation_origin = fields.Char(string="Cotización Origen", readonly=True)

    def _select(self):
        return super(PurchaseReport, self)._select() + ", po.quotation_origin as quotation_origin"

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + ", po.quotation_origin"
