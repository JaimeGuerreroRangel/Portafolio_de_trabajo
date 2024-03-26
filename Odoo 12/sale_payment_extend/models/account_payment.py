# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime
import pytz

class AccountPayment(models.Model):
    _inherit = 'account.payment'
    _description = 'Payment'
    
    sale_order_domain = fields.Many2many(
        'sale.order', 
        compute='_compute_sale_order_domain'
    )

    sale_ids_advance_payment = fields.Many2many(
        'sale.order', 
        'payment_sale_advance_rel', 
        'payment_id', 
        'sale_id', 
        string='Ventas relacionadas con este anticipo',
        domain="[('id', 'in', sale_order_domain)]"
    )

    @api.depends('partner_id')
    def _compute_sale_order_domain(self):
        for record in self:
            if record.partner_id:
                sale_orders = self.env['sale.order'].search([
                    ('partner_id', '=', record.partner_id.id),
                    ('state', 'in', ['done', 'awaiting_payment'])
                ])
                record.sale_order_domain = sale_orders
            else:
                record.sale_order_domain = self.env['sale.order']

    payment_customer_advanced = fields.Boolean('Anticipo CFDI', default=False, help="Considerar este pago como anticipo fiscal por lo que podrá ser timbrado para obtener un CFDI")
    
    @api.multi            
    def post(self):
        for rec in self:
            if rec.payment_customer_advanced and not self.env.user.has_group('sale_cash_payment_term_extend.admin_advance_payment'):
                if not rec.sale_ids_advance_payment:
                    raise UserError("Cuando el pago de anticipo está activado, se requiere al menos una venta relacionada.")
        res = super(AccountPayment, self).post()
        return res
    
    def get_time(self, timestamp):
        utc_time = pytz.utc.localize(timestamp)
        user_tz = pytz.timezone('Etc/GMT+6')
        return utc_time.astimezone(user_tz)
    
    @api.model
    def create(self, vals):
        # Obtener el usuario actual
        current_user = self.env.user.name
        # Obtener la fecha y hora actual
        current_datetime = fields.Datetime.now()
        time = self.get_time(current_datetime)
        formatted_date = time.strftime("%d-%m-%Y")
        formatted_time = time.strftime("%H:%M:%S")
        
        res = super(AccountPayment, self).create(vals)
        
        for rec in res:
            if rec.sale_ids_advance_payment and rec.payment_customer_advanced:
                message = "El usuario {} añadió las siguientes ventas {} al anticipo, el {} a las {}".format(current_user, rec.sale_ids_advance_payment.mapped('name'), formatted_date, formatted_time)
                rec.message_post(body=message)
        return res
    
    @api.multi
    def write(self, vals):
        # Obtener el usuario actual
        current_user = self.env.user.name
        # Obtener la fecha y hora actual
        current_datetime = fields.Datetime.now()
        time = self.get_time(current_datetime)
        formatted_date = time.strftime("%d-%m-%Y")
        formatted_time = time.strftime("%H:%M:%S")

        # Guardar los valores antiguos de 'sale_ids_advance_payment'
        old_values_dict = {rec.id: rec.sale_ids_advance_payment.mapped('name') for rec in self}

        res = super(AccountPayment, self).write(vals)

        for rec in self:
            if 'sale_ids_advance_payment' in vals:
                # Comparar los valores nuevos con los antiguos
                new_values = rec.sale_ids_advance_payment.mapped('name')
                old_values = old_values_dict[rec.id]
                added_values = set(new_values) - set(old_values)
                removed_values = set(old_values) - set(new_values)

                if added_values and rec.payment_customer_advanced:
                    added_values_str = ", ".join(added_values)
                    add_message = "El usuario {} agregó las siguientes ventas [{}] al anticipo, el {} a las {}".format(current_user, added_values_str, formatted_date, formatted_time)
                    rec.message_post(body=add_message)

                if removed_values and rec.payment_customer_advanced:
                    removed_values_str = ", ".join(removed_values)
                    remove_message = "El usuario {} eliminó las siguientes ventas [{}] del anticipo, el {} a las {}".format(current_user, removed_values_str, formatted_date, formatted_time)
                    rec.message_post(body=remove_message)
        return res