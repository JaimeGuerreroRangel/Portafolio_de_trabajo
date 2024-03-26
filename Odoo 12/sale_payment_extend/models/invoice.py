# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False):
        res = super(AccountInvoice, self).register_payment(payment_line,writeoff_acc_id,writeoff_journal_id)
        for invoice in self:
            paid_percentage = round((invoice.residual *100) / invoice.amount_total)
            if paid_percentage < 50.0:
                sale_rows = invoice.env['sale.order']
                for inv_line_row in invoice.invoice_line_ids:
                    for sale_line_row in inv_line_row.sale_line_ids:
                        if sale_line_row.order_id.state == 'awaiting_payment':
                            sale_rows |= sale_line_row.order_id
                if sale_rows:
                    sale_rows.action_apply_payment()
        return res
    
    
    def create_invoice_advance(self):
        self.ensure_one()
        if self.invoice_manual_rel_ids:
            raise UserError(_(u"Aviso !\n\nNo puede agregar archivos relacionados si ya se aagregaron anticipos manuales."))
        if not self.cfdi_type_rel:
            raise UserError(_(u"Aviso !\n\nNo puede agregar archivos relacionados si no ha seleccionado tipo de relación."))
        # if self.type == 'out_invoice' and self.cfdi_type_rel in ('01','02'):
        #     raise UserError(_(u"Aviso !\n\nNo puede agregar relacionados con tipo de relación 01 y 02 para una factura de cliente."))
        elif self.type == 'out_refund' and self.cfdi_type_rel not in ('01','02','04'):
            raise UserError(_(u"Aviso !\n\nNo puede agregar relacionados con tipo de relación diferente a 01, 02 y 04 para notas de credito."))

        # Se crea el wizard
        vals = {
            'partner_id': self.partner_id.id,
            'invoice_id':self.id
        }
        wizard_id = self.env['select.invoice.advanced.wizard'].create(vals)
        advance_payment_sale_limitation = self.company_id.advance_payment_sale_limitation
        if advance_payment_sale_limitation:
            if self.cfdi_type_rel == '07':
                related_sale_ids = self.env['sale.order'].search([('invoice_ids', 'in', [self.id])]).ids
                domain = [('partner_id','=',self.partner_id.id),
                          ('state','=', 'posted'),
                          ('payment_customer_advanced','=',True),
                          ('advanced_cfdi_sign','=', True),
                          ('sale_ids_advance_payment', 'in', related_sale_ids)]
                logging.info("\n\n\ndomain: {}".format(domain))
                advanced_rows = self.env['account.payment'].search(domain)
                for advanced_row in advanced_rows:
                    residual = 0.0
                    for line in advanced_row.sudo().move_line_ids:
                        if line.account_id.internal_type in ('receivable', 'payable'):
                            if advanced_row.currency_id == self.currency_id:
                                residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                            else:
                                from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                                residual += advanced_row.company_id.currency_id.compute(line.amount_residual, self.currency_id)
                    residual = abs(residual)

                    if residual > 0.0:
                        residual = self.currency_id.compute(residual, advanced_row.currency_id)
                        amount = self.get_amount_applied_cfdi_rel(advanced_row, residual)
                        val = {
                            'wizard_id': wizard_id.id,
                            'payment_rel_id': advanced_row.id,
                            'selected': False,
                            'amount': advanced_row.amount,
                            'amount_residual': residual,
                            'amount_applied': amount,
                            'currency_id': advanced_row.currency_id.id,
                        }
                        self.env['invoice.advanced.line'].create(val)
                # Devolvemos el wizard
                return {
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'select.invoice.advanced.wizard',
                    'views': [(self.env.ref('experts_account_invoice_cfdi_33.select_invoice_advanced_wizard_id').id, 'form')],
                    'res_id': wizard_id.id,
                    'target': 'new',
                }
        if self.cfdi_type_rel == '07':
            # Buscamos los anticipos del cliente
            domain = [('partner_id','=',self.partner_id.id),
                      ('state','=', 'posted'),
                      ('payment_customer_advanced','=',True),
                      ('advanced_cfdi_sign','=', True)]
            # advanced_rows = self.env['account.invoice.advanced'].search(domain)
            advanced_rows = self.env['account.payment'].search(domain)
            for advanced_row in advanced_rows:
                residual = 0.0
                for line in advanced_row.sudo().move_line_ids:
                    if line.account_id.internal_type in ('receivable', 'payable'):
                        if advanced_row.currency_id == self.currency_id:
                            residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                        else:
                            from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                            residual += advanced_row.company_id.currency_id.compute(line.amount_residual, self.currency_id)
                residual = abs(residual)

                if residual > 0.0:
                    residual = self.currency_id.compute(residual, advanced_row.currency_id)
                    amount = self.get_amount_applied_cfdi_rel(advanced_row, residual)
                    val = {
                        'wizard_id': wizard_id.id,
                        'payment_rel_id': advanced_row.id,
                        'selected': False,
                        'amount': advanced_row.amount,
                        'amount_residual': residual,
                        'amount_applied': amount,
                        'currency_id': advanced_row.currency_id.id,
                    }
                    self.env['invoice.advanced.line'].create(val)
            # Devolvemos el wizard
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'select.invoice.advanced.wizard',
                'views': [(self.env.ref('experts_account_invoice_cfdi_33.select_invoice_advanced_wizard_id').id, 'form')],
                'res_id': wizard_id.id,
                'target': 'new',
            }
        if self.cfdi_type_rel in ('01','02','03'):
            # Buscamos los anticipos del cliente
            domain = [('partner_id','=',self.partner_id.id),('state','=', 'open'),('inv_advanced','=',False),('type','=','out_invoice')]
            invoice_rows = self.env['account.invoice'].search(domain)
            for invoice_row in invoice_rows:
                # amount = self.get_amount_applied_cfdi_rel(advanced_row)
                val = {
                    'wizard_id': wizard_id.id,
                    'invoice_rel_id': invoice_row.id,
                    'selected': False,
                    'amount_applied': 0.0,
                }
                self.env['invoice.advanced.line'].create(val)
            # Devolvemos el wizard
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'select.invoice.advanced.wizard',
                'views': [(self.env.ref('experts_account_invoice_cfdi_33.select_invoice_advanced_wizard_id_refund').id, 'form')],
                'res_id': wizard_id.id,
                'target': 'new',
            }
        else:
            # Devolvemos el wizard
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'select.invoice.advanced.wizard',
                'views': [(self.env.ref('experts_account_invoice_cfdi_33.select_invoice_advanced_wizard_id_uuid_rel').id, 'form')],
                'res_id': wizard_id.id,
                'target': 'new',
            }