# -*- encoding: utf-8 -*-

from odoo import fields, models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def print_stock_delivery(self):
        return self.env.ref('stock_reports.action_report_delivery').report_action(self)
    
    def print_stock_picking(self):
        return self.env.ref('stock_reports.action_report_picking').report_action(self)
    
    