# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
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
                    'quotation.purchase.order', sequence_date=seq_date) or _("New")
        return super().create(vals_list)
    
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.state == 'purchase' or order.state == 'done':
                if not order.quotation_origin:
                    order.quotation_origin = order.name
                    order.name = self.env['ir.sequence'].next_by_code('purchase.order') or _('New')
                    if order.picking_ids:
                        order.picking_ids.write({'origin':order.name})
        return res