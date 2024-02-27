# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        #Obtener almacenes permitidos por usuario
        allowed_warehouses = self.env.user.warehouse_ids_validate
        if self.picking_type_id.code in ['incoming', 'outgoing', 'internal', 'mrp_operation']:
            if self.picking_type_id.warehouse_id not in allowed_warehouses:
                raise UserError(_('No puedes realizar movimientos de este almacén, contacta al administrador.'))
        return super(StockPicking, self).button_validate()

    
    def action_cancel(self):
        #Obtener almacenes permitidos por usuario
        allowed_warehouses = self.env.user.warehouse_ids_validate
        if self.picking_type_id.code in ['incoming', 'outgoing', 'internal', 'mrp_operation']:
            if self.picking_type_id.warehouse_id not in allowed_warehouses:
                raise UserError(_('No puedes realizar movimientos de este almacén, contacta al administrador.'))
        return super(StockPicking, self).action_cancel()
    
    
class StockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    def action_validate(self):
        #Obtener almacenes permitidos por usuario
        allowed_warehouses = self.env.user.warehouse_ids_validate
        
        for scrap in self:
            if scrap.location_id.warehouse_id not in allowed_warehouses:
                raise UserError(_('No puedes realizar movimientos de este almacén, contacta al administrador.'))
                
        return super(StockScrap, self).action_validate()
    