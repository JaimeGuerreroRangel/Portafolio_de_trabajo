# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    gift_added = fields.Boolean(string="Regalo añadido en la orden de venta", default=False, copy=False)
    
    def action_confirm(self):
        for order in self:
            if order.company_id.this_company_give_gift:

                # Asegúrate de que el producto de regalo esté configurado
                product_gift_template_id = self.env.company.product_gift.id
                
                # Verifica que el producto de regalo esté configurado en la compañía
                product_gift_product = self.env['product.product'].search([
                    ('product_tmpl_id', '=', product_gift_template_id),
                    ('company_id', '=', self.env.company.id)
                ], limit=1)

                # Asegúrate de que product_gift_product es válido antes de continuar
                if not product_gift_product:
                    raise UserError(_("El producto de regalo no se encuentra o no está configurado correctamente."))
                
                if not order.gift_added and product_gift_template_id and not order.partner_id.gift:
                    if any(line.product_id.product_tmpl_id.give_gift for line in order.order_line):
                        self.env['sale.order.line'].create({
                            'order_id': order.id,
                            'product_id': product_gift_product.id,
                            'name': product_gift_product.name or _('Regalo'),
                            'product_uom': product_gift_product.uom_id.id,
                            'price_unit': product_gift_product.lst_price,
                            'product_uom_qty': 1,
                            'discount': 100,
                            'tax_id': [(6, 0, [])],
                            'warehouse_id': order.warehouse_id.id,
                        })
                        order.partner_id.write({'gift': True})
                        order.write({'gift_added': True})
                        
        return super(SaleOrder, self).action_confirm()