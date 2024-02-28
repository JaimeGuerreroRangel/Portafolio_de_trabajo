# -*- encoding: utf-8 -*-

from datetime import datetime
from odoo import models, fields, api
import pytz


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Para la pestaña de Ventas y Compras
    # Agregamos una lista de los campos que se pueden modificar
    
    sale_purchase = ['customer', 'notify_email', 'opt_out', 'message_bounce','border_stimulus','send_statement_report',
             'property_product_pricelist', 'property_stock_customer', 'property_stock_supplier', 'supplier',
             'paymen_notification', 'foreign_supplier', 'account_account_id', 'property_purchase_currency_id', 
             'percentage_commission']
    
    # Para la pestaña de Datos de Contacto
    customers = ['name', 'street', 'street2', 'l10n_mx_street3', 'l10n_mx_street4', 'l10n_mx_city2', 'city',
                 'state_id', 'zip', 'country_id', 'email', 'payment_terms_ids']
    
    # Creamos un diccionario para mostrar los nombres de las variables en la vista
    
    name_map = {
        'customer': u'Es Cliente',
        'notify_email': u'Enviar mensajes y notificaciones',
        'opt_out': u'No acepta mensajes',
        'message_bounce': u'Rebote',
        'border_stimulus': u'Estimulo fronterizo',
        'send_statement_report': u'Enviar estado de cuenta por email',
        'property_product_pricelist': u'Tarifa de venta',
        'property_stock_customer': u'Ubicación del cliente',
        'property_stock_supplier': u'Ubicación del proveedor',
        'supplier': u'Es Proveedor',
        'paymen_notification': u'Avisar de pagos a proveedor',
        'foreign_supplier': u'Proveedor Extranjero',
        'account_account_id': u'Cuenta de gastos por defecto',
        'property_purchase_currency_id': u'Moneda de Proveedor',
        'percentage_commission': u'Porcentaje de Comisión',
        'name': u'Nombre', # Campos de la pestaña de Datos de Contacto
        'street': u'Calle',
        'street2': u'Calle 2',
        'l10n_mx_street3': u'Número exterior',
        'l10n_mx_street4': u'Interior',
        'l10n_mx_city2': u'Municipio',
        'city': u'Colonia',
        'state_id': u'Estado',
        'zip': u'Código Postal',
        'country_id': u'País',
        'email': u'Correo electrónico',
        'payment_terms_ids': u'Términos de pago',
    }
    
    # Diccionario para cambiar True y False 
    
    boolean_map = {
        True: u'Activo',
        False: u'Inactivo',
    }
    
    # Diccionario para cambiar el campo selection
    
    selection_map = {
        'none': u'Nunca',
        'always': u'Todos los mensajes',
    }
    
    # Creamos una lista de todos los campos many2one
    
    many2one_list = ['property_product_pricelist', 'property_stock_customer', 'property_stock_supplier',
                     'property_purchase_currency_id', 'account_account_id', 'state_id', 'country_id']
    
    # Creamos un diccionario para los campos many2one con su campo relacionado
        
    many2one_model = {
        'property_product_pricelist': 'product.pricelist',
        'property_stock_customer': 'stock.location',
        'property_stock_supplier': 'stock.location',
        'property_purchase_currency_id': 'res.currency',
        'account_account_id': 'account.account',
        'state_id': 'res.country.state',
        'country_id': 'res.country',
    }
    
    # Creamos una lista de los campos many2many
    
    many2many_list = ['payment_terms_ids']
    
    # Creamos un diccionario para los campos many2many con su campo relacionado
    
    many2many_model = {
        'payment_terms_ids': 'account.payment.term',
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
                if field in record.sale_purchase or field in record.customers: # Aquí comprueba si pertenece a una de las listas
                    old_value = getattr(record, field) # Obtenemos los valores anteriores
                    tracking_values[field] = (old_value, value) # Guardamos los valores anteriores y los nuevos
        
            # Aquí se crean los mensajes que se mostraran en el message_post
            messages = [] # Lista para guardar los mensajes
            if tracking_values:
                for field, values in tracking_values.items(): # Recorremos los valores del diccionario
                    if field in record.many2one_list: # Comprobamos si pertenece a la lista de many2one
                        model = record.many2one_model[field] # Obtenemos el modelo
                        m2o_record = record.env[model].browse(values[0].id) if values[0] else None # Obtenemos el registro anterior
                        # Aquí para property_product_pricelist hacemos una condición de mostrar nombre y moneda
                        # Si no es property_product_pricelist solo mostramos el nombre
                        if field == 'property_product_pricelist' and m2o_record and m2o_record.currency_id: 
                            old_value = u"{} ({})".format(m2o_record.name, m2o_record.currency_id.name)
                        else:
                            old_value = m2o_record.name if m2o_record else ''
                        # Valores nuevos
                        m2o_record = self.env[model].browse(values[1]) if values[1] else None
                        if field == 'property_product_pricelist' and m2o_record and m2o_record.currency_id:
                            new_value = u"{} ({})".format(m2o_record.name, m2o_record.currency_id.name)
                        else:
                            new_value = m2o_record.name if m2o_record else ''
                        # Mensaje    
                        messages.append(u"El campo '{field}' cambio de '{old}' a '{new}'.".format(
                            field=self.name_map.get(field, field),
                            old=old_value,
                            new=new_value,
                        ))
                    # Para el campo many2many    
                    elif field in record.many2many_list:
                        model = record.many2many_model[field]
                        # Inicializamos las listas para los valores antiguos y nuevos
                        old_records = getattr(record, field)
                        old_values = ', '.join(old_records.mapped('name')) # Une los valores antiguos para mostrarlos
                        
                        # Valores nuevos
                        # Iniciamos una lista para guardar los valores nuevos
                        # number_id es el id del registro en el modelo 
                        #'_' actua como una variable para guardar el valor de number_id que 
                        # desempaqueta la tupla.
                        # ids es el id del registro en el modelo many2many
                        #4: Añade un registro existente al conjunto.
                        #5: Elimina todos los registros del conjunto (sin eliminarlos de la base de datos).
                        #6: Reemplaza el conjunto con un conjunto específico de registros.
                        new_ids = []
                        for number_id, _, ids in vals[field]:
                            if number_id in [4, 6]:  # add or replace
                                if isinstance(ids, list):
                                    new_ids.extend(ids)
                                else:
                                    new_ids.append(ids)
                            elif number_id == 5:  # delete
                                new_ids = []
                        new_records = self.env[model].browse(new_ids)
                        new_values = ', '.join(new_records.mapped('name'))  # Une los valores nuevos para mostrarlos
                        messages.append(u"En los '{field}' se cambio de '{old}' a '{new}'.".format(
                            field=record.name_map.get(field, field),
                            old=old_values,
                            new=new_values,
                        ))
                    # Para el campo selection
                    elif field in ['notify_email']:
                        old_value = self.selection_map.get(values[0], values[0])
                        new_value = self.selection_map.get(values[1], values[1])
                        messages.append(u"El campo '{field}' cambio de '{old}' a '{new}'.".format(
                            field=self.name_map.get(field, field),
                            old=old_value,
                            new=new_value,
                        ))
                    # Para los demás campos Char, Integer
                    else:
                        old_value = '' if values[0] is False else values[0]
                        new_value = values[1]
                        messages.append(u"Se modifico el campo '{field}' '{old}' a '{new}'.".format(
                            field=self.name_map.get(field, field),
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
            super(ResPartner, record).write(vals)    
        return True