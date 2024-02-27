# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    quotation_origin = fields.Char('Cotización Origen', copy=False, default='')
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'company_id' in vals:
                self = self.with_company(vals['company_id'])
            if vals.get('name', _("New")) == _("New"):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['date_order'])
                ) if 'date_order' in vals else None
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'quotation.sale.order', sequence_date=seq_date) or _("New")
        return super().create(vals_list)
    
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.state == 'sale':
                if not order.quotation_origin:
                    order.quotation_origin = order.name
                    order.name = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
                    if order.picking_ids:
                        order.picking_ids.write({'origin':order.name})
        return res