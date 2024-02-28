# -*- encoding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api
import pytz


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Para la pestaña de Contabilidad
    # Agregamos una lista de los campos que se pueden modificar
        
    accounting = ['credit_limit', 'trust', 'property_account_position_id', 'reg_fis_id', 'uso_cfdi_id', 'forma_pago_id',
                  'met_pago_id', 'vat', 'reg_trib', 'is_driver', 'driver_license', 'property_supplier_payment_term_id', 
                  'property_account_receivable_id', 'property_account_payable_id', 
                  'number_fiscal_id_diot', 'nacionality_id', 'type_of_third', 'type_of_operation']
    
    # Creamos un diccionario para mostrar los nombres de las variables en la vista
    
    name_map_acc = {
        'credit_limit': u'Crédito concedido',
        'trust': u'Grado de confianza para este deudor',
        'property_account_position_id': u'Posición fiscal',
        'reg_fis_id': u'Regimen fiscal SAT',
        'uso_cfdi_id': u'Uso de CFDI',
        'forma_pago_id': u'Forma de pago',
        'met_pago_id': u'Método de pago',
        'vat': u'RFC',
        'reg_trib': u'Regimen tributario SAT',
        'is_driver': u'Es operador de Camión',
        'driver_license': u'No. de licencia',
        'property_supplier_payment_term_id': u'Plazo de pago de proveedor',
        'property_account_receivable_id': u'Cuenta a cobrar',
        'property_account_payable_id': u'Cuenta a pagar',
        'number_fiscal_id_diot': u'Número fiscal (DIOT)',
        'nacionality_id': u'Nacionalidad (DIOT)',
        'type_of_third': u'Tipo de tercero (DIOT)',
        'type_of_operation': u'Tipo de operación (DIOT)',
    }
    
    # Diccionario para cambiar True y False 
    boolean_map_acc = {
        True: u'Activo',
        False: u'Inactivo',
    }
    
    # Diccionario para cambiar los valores de la lista de selección
    selection_map_acc = {
        'good': u'Buen pagador',
        'normal': u'Pagador normal',
        'bad': u'Mal pagador',
        '04': u'04 Proveedor nacional',
        '05': u'05 Proveedor extranjero',
        '15': u'15 Proveedor global',
        '03': u'03 Prestación de Servicios Profesionales',
        '06': u'06 Arrendamiento de inmuebles',
        '85': u'85 Otros',
    }
    
    # Lista de campos que son de tipo many2one
    many2one_list_acc = ['property_account_position_id', 'reg_fis_id', 'uso_cfdi_id', 'forma_pago_id',
                            'met_pago_id', 'property_supplier_payment_term_id', 'property_account_receivable_id', 
                            'property_account_payable_id']
    
    # Diccionario para cambiar los valores de los campos many2one
    many2one_model_acc = {
        'property_account_position_id': 'account.fiscal.position',
        'reg_fis_id': 'res.reg.fiscal',
        'uso_cfdi_id': 'res.uso.cfdi',
        'forma_pago_id': 'res.forma.pago',
        'met_pago_id': 'res.met.pago',
        'property_supplier_payment_term_id': 'account.payment.term',
        'property_account_receivable_id': 'account.account',
        'property_account_payable_id': 'account.account',
    }
    
    # Agregamos para fecha actual
    def get_time(self, timestamp):
        utc_time = pytz.utc.localize(timestamp)
        user_tz = pytz.timezone('Etc/GMT+6')
        return utc_time.astimezone(user_tz)
    
    # Aqui se realiza el seguimiento de los cambios
    @api.multi
    def write(self, vals):
        for record in self:
            tracking_values = {} # Diccionario para guardar los valores que se modificaron
            for field, value in vals.items(): # Recorremos los valores que se modificaron
                if field in record.accounting: # Aquí comprueba si pertenece a la lista
                    old_value = getattr(record, field) # Obtenemos los valores anteriores
                    tracking_values[field] = (old_value, value) # Guardamos los valores anteriores y los nuevos
        
            # Aquí se crean los mensajes que se mostraran en el message_post
            messages = [] # Lista para guardar los mensajes
            if tracking_values:
                for field, values in tracking_values.items(): # Recorremos los valores del diccionario
                    if field in record.many2one_list_acc: # Comprobamos si pertenece a la lista de many2one
                        model = record.many2one_model_acc[field] # Obtenemos el modelo
                        m2o_record = record.env[model].browse(values[0].id) if values[0] else None # Obtenemos el registro anterior
                        # Aquí se crea la condición de agregar tanto el nombre como la descripción y sea
                        # Visible en el mensaje
                        if field in ['reg_fis_id', 'uso_cfdi_id', 'forma_pago_id', 'met_pago_id'] and m2o_record and m2o_record.description:
                            old_value = u"{}-{}".format(m2o_record.name, m2o_record.description)
                        else:
                            old_value = m2o_record.name if m2o_record else ''
                        
                        # Valor nuevo
                        m2o_record = self.env[model].browse(values[1]) if values[1] else None
                        if field in ['reg_fis_id', 'uso_cfdi_id', 'forma_pago_id', 'met_pago_id'] and m2o_record and m2o_record.description:
                            new_value = u"{}-{}".format(m2o_record.name, m2o_record.description)
                        else:
                            new_value = m2o_record.name if m2o_record else ''
                        messages.append(u"El campo '{field}' cambio de '{old}' a '{new}'.".format(
                            field=self.name_map_acc.get(field, field),
                            old=old_value,
                            new=new_value,
                        ))
                    # Para los campos que son booleanos
                    elif field in ['is_driver']:
                        old_value = self.boolean_map_acc.get(values[0], values[0])
                        new_value = self.boolean_map_acc.get(values[1], values[1])
                        messages.append(u"El campo '{field}' cambio de estado '{old}' a '{new}'.".format(
                            field=self.name_map_acc.get(field, field),
                            old=old_value,
                            new=new_value,
                        ))   
                    # Para los campos que son de tipo selection    
                    elif field in ['trust', 'type_of_third', 'type_of_operation']:
                        old_value = self.selection_map_acc.get(values[0], values[0])
                        new_value = self.selection_map_acc.get(values[1], values[1])
                        messages.append(u"El campo '{field}' cambio de '{old}' a '{new}'.".format(
                            field=self.name_map_acc.get(field, field),
                            old=old_value,
                            new=new_value,
                        ))
                    # Para los demás campos
                    else:
                        old_value = '' if values[0] is False else values[0]
                        new_value = values[1]
                        messages.append(
                        u"Se modifico el campo '{field}' '{old}' a '{new}'.".format(
                            field=self.name_map_acc.get(field, field),
                            old=old_value,
                            new=new_value,
                        ))
            # Aquí se crea el mensaje con los cambios que se realizaron             
            if messages:
                now_utc = datetime.now()
                time = record.get_time(now_utc)
                formatted_time = time.strftime('%d/%m/%Y %H:%M:%S')
                body = u"En fecha {date}, se realizaron los siguientes cambios:<br/> - {messages}".format(
                    date=formatted_time,
                    messages="<br/> - ".join(messages)
                )
                record.message_post(body=body)
            
            if record.comment and vals.get('comment'):
                msg = "Nota modificada para " + record.name + "<ul><p></p>"
                msg += "<li>Nota anterior: " + record.comment
                msg += "<li>Nota nueva: " + vals['comment'] + "</ul>"
                record.message_post(body=msg)
            elif not record.comment and vals.get('comment'):
                msg = "Nota agregada para " + record.name + "<ul><p></p>"
                msg += "<li>Nota interna: " + vals['comment'] + "</ul>"
                record.message_post(body=msg)
            super(ResPartner, record).write(vals)
        return True 