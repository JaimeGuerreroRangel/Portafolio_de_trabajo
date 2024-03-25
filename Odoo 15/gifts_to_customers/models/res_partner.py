# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    gift = fields.Boolean(string="Regalo", default=False, help="Si este campo esta activo, significa que el cliente ya recibio su regalo")
    
    
    # Función para actualizar el campo gift en los clientes, solo cuando se instala el módulo
    @api.model
    def initialize_module(self):
        # Verificar si el módulo ya fue inicializado
        initizalize = self.env['ir.config_parameter'].sudo().get_param('gifts_to_customers.initialize', False)
        
        if not initizalize:
            self.env.cr.execute("UPDATE res_partner SET gift = TRUE WHERE gift IS NOT TRUE")
            # Marca el módulo como inicializado
            self.env['ir.config_parameter'].sudo().get_param('gifts_to_customers.initialize', True)
    