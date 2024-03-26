# -*- encoding: utf-8 -*-

from odoo import _, api, fields, models

class ResCompany(models.Model):
    _inherit = 'res.company'
    
    advance_payment_sale_limitation = fields.Boolean('Limita el tipo de relación en la factura', 
                                                     help="""Al tener activo este campo, se limitará el tipo de relación de la factura a solo mostrando 
                                                     los que tenga los anticipos que la venta tenga relacionados.""", default=False)