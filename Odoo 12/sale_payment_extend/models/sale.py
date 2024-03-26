# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.addons import decimal_precision as dp
from functools import partial
from odoo.tools.misc import formatLang
from odoo.tools.float_utils import float_compare
from datetime import datetime
import pytz
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    advanced_payment_ids = fields.Many2many(
        'account.payment', 
        'sale_advance_payment_rel', 
        'sale_id', 
        'payment_id', 
        string='Anticipos relacionados', 
        domain=[('payment_customer_advanced', '=', True)], 
        compute='_compute_advanced_payment_ids',
    )

    def _compute_advanced_payment_ids(self):
        for record in self:
            advanced_payments = self.env['account.payment'].search([
                ('partner_id', '=', record.partner_id.id),
                ('payment_customer_advanced', '=', True),
                ('state', '=', 'posted'),
                ('advanced_cfdi_sign', '=', True),
                ('sale_ids_advance_payment', 'in', record.id)
            ])
            record.advanced_payment_ids = [(6, 0, advanced_payments.ids)]

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        if self.state == "awaiting_payment":
            self.state = 'sale'
            sale_inv_obj = self.env['sale.advance.payment.inv']
            sale_inv_row = sale_inv_obj.create({'advance_payment_method':'all'})
            sale_inv_row.with_context(active_id = self.id, active_ids = [self.id]).create_invoices()
            self.state = 'awaiting_payment'
            for inv_row in self.invoice_ids:
                if inv_row.state == 'draft':
                    inv_row.action_invoice_open()
        else:
            if not self.invoice_ids:
                sale_inv_obj = self.env['sale.advance.payment.inv']
                sale_inv_row = sale_inv_obj.create({'advance_payment_method':'all'})
                sale_inv_row.with_context(active_id = self.id, active_ids = [self.id]).create_invoices()
                for inv_row in self.invoice_ids:
                    if inv_row.state == 'draft':
                        inv_row.action_invoice_open()
        return res

    @api.multi
    def action_cancel(self):
        for sale_row in self:
            if sale_row.state == 'awaiting_payment':
                if sale_row.invoice_ids:
                    for inv_row in sale_row.invoice_ids:
                        if inv_row.state != 'cancel':
                            if inv_row.payment_move_line_ids:
                                inv_row.payment_move_line_ids.remove_move_reconcile()
                            inv_row.action_invoice_cancel()
        return super(SaleOrder, self).action_cancel()
    
    @api.multi
    def cron_check_so_awaiting_payment(self):
        sale_notify_rows = sale_cancel_rows = self.env['sale.order']
        so_rows = self.search([('state','=', 'awaiting_payment')])
        date_now = datetime.now()
        
        for sale_row in so_rows:
            date_diff = date_now - sale_row.confirmation_date
            
            if date_diff.days >= sale_row.company_id.set_aside_days:
                # Se verifica si la venta tiene anticipos relacionados en el campo sale_ids_advance_payment
                if not sale_row.advanced_payment_ids:
                    sign_invoice = False
                    for invoice in sale_row.invoice_ids:
                        if invoice.sign or invoice.invoice_advanced_rel_ids or invoice.amount_total != invoice.residual:
                            sign_invoice = True
                            break
                    if not sign_invoice:
                        sale_cancel_rows |= sale_row
            elif date_diff.days >= sale_row.company_id.warning_days:
                sale_notify_rows |= sale_row
        if sale_cancel_rows:
            try:
                sale_cancel_rows.action_cancel()
            except:
                logging.info(u"Error al cancelar ventas pendientes de pago")
        if sale_notify_rows:
            try:
                sale_notify_rows.send_alert_sale_awaiting_payment()
            except:
                logging.info(u"Error al enviar alertas de ventas pendientes de pago")
        return True