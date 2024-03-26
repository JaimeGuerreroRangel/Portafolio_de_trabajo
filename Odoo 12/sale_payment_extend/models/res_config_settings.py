# -*- encoding: utf-8 -*-

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    advance_payment_sale_limitation = fields.Boolean('Limita el tipo de relación en la factura', readonly=False, related='company_id.advance_payment_sale_limitation', 
                                                     help="""Al tener activo este campo, se limitará el tipo de relación de la factura a solo mostrando 
                                                     los que tenga los anticipos que la venta tenga relacionados.""")