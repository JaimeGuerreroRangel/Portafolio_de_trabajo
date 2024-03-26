# -*- encoding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import base64
from io import BytesIO
import xlwt
import pytz

class ExcelExportWizard(models.TransientModel):
    _name = 'excel.export.wizard'
    _description = 'Asistente para reporte de trazabilidad'

    def _default_location_id(self):
        location_id = False
        wearehouse_row = self.env['stock.warehouse'].search([('code','=', 'GDL')],limit=1)
        if wearehouse_row:
            location_id = wearehouse_row.lot_stock_id.id
        return location_id

    # Campos para el archivo de Excel
    data_file = fields.Binary(string='Reporte Trazabilidad', readonly=True)
    file_name = fields.Char(string='Excel File', size=64)
    
    # Campos para el popup
    product_id = fields.Many2one('product.product', string='Producto', default=False, 
                                 help='Seleccione un producto')
    location_id = fields.Many2one('stock.location', string='Ubicación', default=False, help='Seleccione un almacén')
    start_date = fields.Date(string='Fecha Inicio', default=False,
                             help='Puede seleccionar una fecha de inicio para el reporte. Si no selecciona una fecha, se tomará el primer movimiento.')
    end_date = fields.Date(string='Fecha Fin', default=fields.Date.today(), help='Se pone por defecto la fecha actual.')
    # Función para validar que se haya seleccionado un producto 
    @api.onchange('location_id')
    def _onchange_location_id(self):
        if self.location_id and not self.product_id:
            self.location_id = False
            return {'warning': {
                'title': ('!Alerta!'),
                'message': _('Seleccione primero un producto, despúes puede seleccionar el almacen.')
            }}

    # Función para mostrar los almacenes donde el producto ha tenido movimientos
    @api.onchange('product_id')
    def _onchange_product(self):
        if not self.product_id:
            return
        # Encuentra los movimientos de stock que involucran el producto seleccionado.
        stock_moves = self.env['stock.move'].search([('product_id', '=', self.product_id.id)])
        # Extrae los ids de ubicación de los movimientos de stock.
        location_ids = stock_moves.mapped('location_id').ids + stock_moves.mapped('location_dest_id').ids
        location_id = False
        wearehouse_row = self.env['stock.warehouse'].search([('code','=', 'GDL')],limit=1)
        if wearehouse_row:
            location_id = wearehouse_row.lot_stock_id.id
        self.location_id = location_id
        # Actualiza el dominio de 'location_id' para mostrar solo las ubicaciones que tienen el producto.
        return {'domain': {'location_id': [('id', 'in', location_ids)]}}

    def get_invoices(self,move):
        invoices_name = ''
        nc_name = ''
        if move.procurement_id.sale_line_id.invoice_lines:
            for invoice in move.procurement_id.sale_line_id.invoice_lines:
                if invoice.invoice_id.type == 'out_invoice':
                    if invoices_name == '':
                        invoices_name = invoice.invoice_id.display_name
                    else:
                        invoices_name += " // " + invoice.invoice_id.display_name
                if invoice.invoice_id.type == 'out_refund':
                    if nc_name == '':
                        nc_name = invoice.invoice_id.display_name
                    else:
                        nc_name += " " + invoice.invoice_id.display_name +" -//"
        return invoices_name,nc_name


    # Función para que al seleccionar un producto y una ubicación, se autocomplete la fecha de inicio
    @api.onchange('product_id', 'location_id')
    def _onchange_product_location(self):
        if self.product_id and self.location_id:
            # Encuentra el primer movimiento de stock para el producto y ubicación seleccionados.
            stock_move = self.env['stock.move'].search([
            ('product_id', '=', self.product_id.id),
                '|', ('location_id', '=', self.location_id.id),
                ('location_dest_id', '=', self.location_id.id),
            ], order='date', limit=1)
            if stock_move:
                # Convierte la cadena en datetime
                datetime_object = datetime.strptime(stock_move.date, "%Y-%m-%d %H:%M:%S")
                # Toma la parte de la fecha del datetime
                self.start_date = datetime_object.date()
    
    # Función para generar el archivo de Excel
    @api.multi
    def generate_excel_report(self):
        self.ensure_one()
        
        # Campos del nombre del producto
        selected_product = self.product_id
        product_name = selected_product.name
        product_code = selected_product.default_code
        
        # Campos para el almacen
        selected_warehouse = self.location_id
        warehouse_name = selected_warehouse.name
        main_warehouse = selected_warehouse.location_id.name
        
        # Campos para las fechas
        start_date_ex = self.start_date
        end_date_ex = self.end_date
        
        workbook = xlwt.Workbook(encoding='utf-8')
        worksheet = workbook.add_sheet('Trazabilidad')
        # Estilos para celdas
        styleTitle = xlwt.easyxf('font: name Arial, bold 1, height 350, color red; align: wrap yes, vert centre, horiz center;')
        styleName = xlwt.easyxf(('font: name Arial, bold 1, height 240, color black; align: wrap yes,vert centre, horiz center;'))
        styleDescription = xlwt.easyxf(('font: name Arial, bold 1, height 270, color black; align: wrap yes,vert centre, horiz center;'))
        styleDate = xlwt.easyxf(('font: name Arial, bold 1, height 250, color black; align: wrap yes,vert centre, horiz center;'))
        
        # Estilos para celdas de tabla
        styleHeader = xlwt.easyxf(('font: name Calibri, bold 1, height 230, color black; align: wrap yes,vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour orange;'))
        styleText = xlwt.easyxf(('font: name Calibri, height 210, color black; align: wrap yes,vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin;'))
        stylePricesStdr = xlwt.easyxf(('font: name Calibri, bold 1, height 210, color black; align: wrap yes,vert centre, horiz center; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_colour lime;'))
        
        # Define el ancho de las columnas
        worksheet.col(1).width = 4000
        
        # Merge cells
        worksheet.row(5).height_mismatch = True
        worksheet.row(5).height = 500 
        
        # Añade datos a la cabecera de Excel
        worksheet.write_merge(0, 0, 0, 14, u'Reporte de movimientos', styleTitle)
        worksheet.write(2, 0, u'Almacen:', styleName)
        worksheet.write_merge(2, 2, 1, 14, u'{}/{}'.format(main_warehouse, warehouse_name), styleDescription)
        worksheet.write(4, 0, u'Clave:', styleName)
        worksheet.write_merge(4, 4, 1, 14, product_code, styleDescription)
        worksheet.write(6, 0, u'Descripción:', styleName)
        worksheet.write_merge(6, 6, 1, 14, product_name, styleDescription)
        worksheet.write_merge(8, 8, 2, 3, u'Fecha Inicio:', styleName)
        worksheet.write_merge(8, 8, 4, 6, start_date_ex, styleDate)
        worksheet.write_merge(8, 8, 8, 10, u'Fecha Final:', styleName)
        worksheet.write_merge(8, 8, 11, 12, end_date_ex, styleDate)
        
        # Convertir las fechas de inicio y fin a datetime
        start_date_obj = datetime.strptime(self.start_date, '%Y-%m-%d')
        # Ajustar la hora de inicio a las 00:00:00
        start_datetime = datetime.combine(start_date_obj.date(), datetime.min.time())
        end_date_obj = datetime.strptime(self.end_date, '%Y-%m-%d')
        # Ajustar la hora de fin a las 23:59:59
        end_datetime = datetime.combine(end_date_obj.date(), datetime.max.time())

        # Ajustar las horas de inicio y fin a 'Etc/GMT+6' (CDMX)
        user_tz = pytz.timezone('Etc/GMT+6')
        start_datetime = user_tz.localize(start_datetime).astimezone(pytz.utc)
        end_datetime = user_tz.localize(end_datetime).astimezone(pytz.utc)
        
        # Convertir datetime a cadena
        start_datetime_str = start_datetime.strftime('%Y-%m-%d %H:%M:%S')
        end_datetime_str = end_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # Encabezados de la tabla
        headers = ['Consecutivo', 'Fecha', 'Tipo de movimiento', 'Referencia', 'Documento Origen', 'Entrada', 'Salida', 'Stock real', 
                   'Precio Unitario PO en Moneda Extranjera', 'Precio Unitario PO MXN', 'Gastos MXN', 'Gastos', 'Costo en MXN', 'Importe costo partida MXN',
                   'Coste (Costo Promedio) MXN', 'Valor de inventario MXN','Valor de inventario real','Coste real','Facturas','Notas de crédito','Usuario']
        # 13 y 15
        for i, header in enumerate(headers):
            worksheet.write(11, i, header, styleHeader)

        
        # Encuentra los movimientos de stock que involucran el producto seleccionado y la ubicación.
        stock_moves = self.env['stock.move'].search([
            ('product_id', '=', self.product_id.id),
            '|', ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_id.id),
            ('date', '>=', start_datetime_str),
            ('date', '<=', end_datetime_str),
            ('state', '=', 'done'),
        ], order='date')
        
        # Se busca el usuario del sistema
        system_user = self.env.ref('base.user_root')
        
        price_history_data = self.env['product.price.history'].search([
            ('product_id', '=', self.product_id.id),
            ('user_id', '!=', system_user.id), # Se excluye cualquier cambio de precio hecho por el sistema
        ], order='datetime asc')
        
        # Movimientos de stock anteriores al rango de fechas
        stock_moves_previous = self.env['stock.move'].search([
            ('product_id', '=', self.product_id.id),
            '|', ('location_id', '=', self.location_id.id),
            ('location_dest_id', '=', self.location_id.id),
            ('date', '<', start_datetime_str),
            ('state', '=', 'done'),
        ], order='date')
        
        # Con esto se calcula el stock inicial
        stock_init = 0
        for moves in stock_moves_previous:
            if moves.location_dest_id == self.location_id:
                stock_init += moves.product_uom_qty
            elif moves.location_id == self.location_id:
                stock_init -= moves.product_uom_qty
            
        row = 12
        counter = 1
        total_qty = stock_init # Así el stock mantendra su valor en cualquier fecha
        product_tot_qty_available = 0 # Variable para almacenar la cantidad total de productos disponibles
        std_price = 0.0
        last = 0
        for i, move in enumerate(stock_moves):
            date = move.date if move.date else '' # Si no hay fecha, asigna una cadena vacía
            if date:
                # Convertir a objeto de fecha y hora en la zona horaria del usuario
                move_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                move_datetime = move_datetime.replace(tzinfo=pytz.UTC)
                move_datetime = move_datetime.astimezone(user_tz)
                # Formatear la fecha y hora
                formatted_date = move_datetime.strftime('%Y-%m-%d %H:%M:%S')
                # Asignar la fecha y hora formateada a la variable date
                date = formatted_date
            # Movimientos de stock   
            if move.picking_id:
                picking_id_name = move.picking_id.name if move.picking_id.name != 'mrp_operation' else 'Movimiento Interno'
            else:
                # if move.name
                picking_id_name = 'Movimiento Interno'
            
            location_id_usage = move.location_id.usage if move.location_id.usage else '' 
            # Ubicación de destino
            location_dest_id_usage = move.location_dest_id.usage if move.location_dest_id.usage else '' 
            # Variable para almacenar el tipo de movimiento
            output = ''
            # Añade un documento origen si es que el movimiento de stock tiene un documento origen
            origin = move.origin if move.origin else ''
            
            qty = 0 # Variable para almacenar la cantidad de productos
            customer_location = self.env['stock.location'].search([('name', '=', 'Clientes')], limit=1)
            supplier_location = self.env['stock.location'].search([('name', '=', 'Proveedores')], limit=1)
            production_order = self.env['stock.location'].search([('name', '=', 'Producción')], limit=1)
            inventory_adjustment = self.env['stock.location'].search([('name', '=', 'Ajuste de inventario')], limit=1)
            scrap = self.env['stock.location'].search([('name', '=', 'Desechado')], limit=1)
    
            # Compras y ventas
            if move.location_dest_id == customer_location:
                output = "Venta"
                worksheet.write(row, 5, '', styleText)
                worksheet.write(row, 6, "{:.1f}".format(move.product_uom_qty), styleText)
                qty = -move.product_uom_qty
            elif move.location_id == supplier_location:
                output = "Compra"
                worksheet.write(row, 5, "{:.1f}".format(move.product_uom_qty), styleText)
                worksheet.write(row, 6, '', styleText)
                qty = move.product_uom_qty
            elif move.location_id == customer_location:
                output = "Obtenido de Clientes"
                if move.origin_returned_move_id:
                    if move.procurement_id and move.procurement_id.sale_line_id:
                        output = 'Devolución venta'
                    if move.purchase_line_id:
                        output = 'Devolución compra'
                worksheet.write(row, 5, "{:.1f}".format(move.product_uom_qty), styleText)
                worksheet.write(row, 6, '', styleText)
                qty = move.product_uom_qty
                
            #  Ordenes de producción
            elif move.location_dest_id == production_order:
                output = "Salida Orden de Producción"
                worksheet.write(row, 5, '', styleText)
                worksheet.write(row, 6, "{:.1f}".format(move.product_uom_qty), styleText)
                qty = -move.product_uom_qty
            elif move.location_id == production_order:
                output = "Abastecimiento de Orden de Producción"
                worksheet.write(row, 5, "{:.1f}".format(move.product_uom_qty), styleText)
                worksheet.write(row, 6, '', styleText)
                picking_id_name = move.name
                origin = move.group_id.name
                qty = move.product_uom_qty
                
            # Ajustes de inventario
            elif move.location_id == inventory_adjustment:
                output = "Entrada de Ajuste de Inventario"
                if move.inventory_id:
                    if picking_id_name == 'Movimiento Interno':
                        picking_id_name = move.inventory_id.folio
                worksheet.write(row, 5, "{:.1f}".format(move.product_uom_qty), styleText)
                worksheet.write(row, 6, '', styleText)
                qty = move.product_uom_qty
            elif move.location_dest_id == inventory_adjustment:
                output = "Salida a Ajuste de Inventario"
                if move.inventory_id:
                    if picking_id_name == 'Movimiento Interno':
                        picking_id_name = move.inventory_id.folio
                worksheet.write(row, 5, '', styleText)
                worksheet.write(row, 6, "{:.1f}".format(move.product_uom_qty), styleText)
                qty = -move.product_uom_qty       
            elif move.location_dest_id == scrap:
                output = "Salida Desechado"
                worksheet.write(row, 5, '', styleText)
                worksheet.write(row, 6, "{:.1f}".format(move.product_uom_qty), styleText)
                qty = -move.product_uom_qty    
            
            # Tránsitos Internos
            # Entradas
            elif location_id_usage == 'internal' and location_dest_id_usage == 'transit':
                output = "Mov. de Salida en Tránsito interno"
                worksheet.write(row, 5, "{:.1f}".format(move.product_uom_qty), styleText)
                worksheet.write(row, 6, '', styleText)
                qty = move.product_uom_qty
                
            elif location_id_usage == 'transit' and location_dest_id_usage == 'internal':
                output = "Mov. de Entrada en Tránsito Interno"
                worksheet.write(row, 5, '', styleText)
                worksheet.write(row, 6, "{:.1f}".format(move.product_uom_qty), styleText)
                qty = move.product_uom_qty  
                
            total_qty += qty
            # Aquí terminan los movimientos de stock         
            
            # Añade el costo promedio del producto    
            unit_price_mxn = 0
            unit_price_foreign = 0 # Monedas extranjeras
            currency_name = '' # Formato de moneda extranjera
            
            # Obtener la moneda MXN
            mxn_currency = self.env.ref('base.MXN')
            
            # Checar si el movimiento es de compra           
            if move.picking_type_id and move.picking_type_id.code == 'incoming':
                # Movimiento de entrada, buscar en el modelo de orden de compra
                if move.purchase_line_id:
                    # Si la moneda es MXN
                    if move.purchase_line_id.order_id.currency_id == mxn_currency:
                        unit_price_mxn = move.purchase_line_id.price_unit
                    else:
                        unit_price_foreign = move.purchase_line_id.price_unit
                        foreign_currency = move.purchase_line_id.order_id.currency_id
                        unit_price_mxn = foreign_currency.with_context(date=move.purchase_line_id.order_id.date_order).compute(unit_price_foreign, mxn_currency)
                        currency_name = move.purchase_line_id.order_id.currency_id.name
                    
            # Aquí termina la busqueda de precios de compra y venta
            # ********* Calculo de los Gastos
            total_expenses = 0
            percentage = 0
            if move.purchase_line_id.order_id:
                pedimento_ids = move.purchase_line_id.order_id.pedimento_ids
                amount = 0
                qty_order = 0
                qty_received = 0
                total_amount = 0
                purchase_total = 0
                expenses = 0
                invoices = 0
                for pedimento in pedimento_ids:
                    for product in pedimento.expenses_ids:
                        amount += product.amount
                    for product in pedimento.pedimento_product_ids:
                        qty_order += product.qty_order
                    for invoices in pedimento.inv_expenses_ids:
                        if invoices.state in ('open', 'paid'):
                            total_amount += invoices.currency_id.with_context(date=invoices.date_invoice).compute(invoices.amount_total, mxn_currency)
                    for product in pedimento.pedimento_product_ids:
                        qty_received += product.qty_received
                    for purchase in pedimento.purchase_ids:
                        purchase_total += purchase.currency_id.with_context(date=purchase.date_order).compute(purchase.amount_total, mxn_currency)
                
                total_expenses = amount + total_amount
                # Porcentaje de gastos
                if purchase_total:
                    percentage = round((total_expenses/purchase_total)*100,0)
                else:
                    percentage = round((total_expenses/1)*100,0)

            cost_line = 0.0 
            percentage_string = "{:.0%}".format(percentage/100.0) 
            expenses_mxn = ""
            gdl_cost_mnx = 0.0
            if unit_price_mxn and percentage > 0.0:
                expenses_mxn = round(unit_price_mxn * (float(percentage)/100.0),2)
            if unit_price_mxn:
                cost_line = round(unit_price_mxn * move.product_uom_qty,2)
            # Costo GDL promedio
            if unit_price_mxn > 0.0 and expenses_mxn > 0.0 and expenses_mxn != '':
                gdl_cost_mnx = float(unit_price_mxn) + float(expenses_mxn)
            else:
                if unit_price_mxn:
                    gdl_cost_mnx = unit_price_mxn
                elif expenses_mxn:
                    gdl_cost_mnx = expenses_mxn
                else:
                    gdl_cost_mnx = 0.0
            if gdl_cost_mnx:
                cost_line = round(gdl_cost_mnx * move.product_uom_qty,2)
            # Verifica si el movimiento de stock es una compra
            new_std_price = 0
            new_qty_incoming = 0
            if move.picking_type_id.code == 'incoming':
                if not total_qty:
                    total_qty_ext = 1
                else:
                    total_qty_ext = total_qty
                # Calcular el costo promedio
                new_std_price = round(((gdl_cost_mnx + std_price) * (total_qty - move.product_qty)) / total_qty_ext,2)
                std_price = new_std_price
            inventory_valuation = round(total_qty * std_price,2)
            # Usuarios que crearon el movimiento
            username = move.create_uid.name
            invoices_name, nc_name = self.get_invoices(move)
            worksheet.write(row, 0, counter, styleText)
            worksheet.write(row, 1, date, styleText)
            worksheet.write(row, 2, output if output else '', styleText) 
            worksheet.write(row, 3, picking_id_name if picking_id_name else '', styleText)
            worksheet.write(row, 4, origin if origin else '', styleText)
            worksheet.write(row, 7, "{}".format(total_qty) , styleText)
            worksheet.write(row, 8, "${} ({})".format(unit_price_foreign, currency_name) if unit_price_foreign else '', styleText)
            worksheet.write(row, 9, "${}".format(unit_price_mxn) if unit_price_foreign else '', styleText)
            worksheet.write(row, 10, "${}".format(expenses_mxn) if expenses_mxn else '', styleText)
            worksheet.write(row, 11, percentage_string if percentage_string else '', styleText)
            worksheet.write(row, 12, "${}".format(gdl_cost_mnx) if gdl_cost_mnx else '', styleText)
            worksheet.write(row, 13, "${}".format(cost_line) , styleText)
            worksheet.write(row, 14, "${}".format(std_price) , styleText)
            worksheet.write(row, 15, "${}".format(inventory_valuation) , styleText)
            worksheet.write(row, 16, "${}".format(float(last)+float(cost_line)) , styleText)
            if total_qty == 0:
                worksheet.write(row, 17, 0, styleText)
            else:
                worksheet.write(row, 17, "${}".format((float(last)+float(cost_line))/total_qty) , styleText)
            worksheet.write(row, 18, invoices_name, styleText)
            worksheet.write(row, 19,  nc_name, styleText)
            worksheet.write(row, 20, username if username else '', styleText)
            row += 1
            counter += 1

            # Define la fecha del próximo movimiento, o la fecha actual si es el último movimiento
            next_move_date = stock_moves[i+1].date if i < len(stock_moves) - 1 else fields.Datetime.now()

            # Filtra los cambios de precio que ocurrieron después de este movimiento y antes del próximo
            related_price_change = price_history_data.filtered(lambda c: move.date < c.datetime < next_move_date)

            if related_price_change:
                for change in related_price_change:
                    worksheet.write(row, 0, counter, stylePricesStdr)
                    worksheet.write(row, 1, change.datetime, stylePricesStdr)
                    worksheet.write(row, 2, 'Coste Estandar Modificado', stylePricesStdr)
                    # worksheet.write_merge(row, row, 2, 12, 'Coste Estandar Modificado', stylePricesStdr)
                    worksheet.write(row, 3, '', stylePricesStdr)
                    worksheet.write(row, 4, '', stylePricesStdr)
                    worksheet.write(row, 5, '', stylePricesStdr)
                    worksheet.write(row, 6, '', stylePricesStdr)
                    worksheet.write(row, 7, "{}".format(total_qty), stylePricesStdr)
                    worksheet.write(row, 8, '', stylePricesStdr)
                    worksheet.write(row, 9,'', stylePricesStdr)
                    worksheet.write(row, 10, '', stylePricesStdr)
                    worksheet.write(row, 11, '', stylePricesStdr)
                    worksheet.write(row, 12, '', stylePricesStdr)
                    worksheet.write(row, 13, '', stylePricesStdr)
                    worksheet.write(row, 14, "${}".format(change.cost), stylePricesStdr)
                    worksheet.write(row, 15, "${}".format(inventory_valuation), stylePricesStdr)
                    worksheet.write(row, 16, "${}".format(float(last)+float(cost_line)) , stylePricesStdr)
                    if total_qty == 0:
                        worksheet.write(row, 17, 0, stylePricesStdr)
                    else:
                        worksheet.write(row, 17, "${}".format((float(last)+float(cost_line))/total_qty) , stylePricesStdr)
                    worksheet.write(row, 18,'', stylePricesStdr)
                    worksheet.write(row, 19,'', stylePricesStdr)
                    worksheet.write(row, 20, change.user_id.name or "Administrador", stylePricesStdr)
                    std_price = change.cost
                    row += 1
                    counter += 1
            last = inventory_valuation
                    
        # Guarda el archivo de Excel en el buffer
        report = BytesIO() # Tomamos de la librería from io import BytesIO
        workbook.save(report)
        report.seek(0)

        # Crea el archivo Excel y guarda el archivo en el campo 'data_file'
        self.file_name = 'Trazabilidad.xls'
        self.data_file = base64.b64encode(report.read())

        # Restablecer campos o valores necesarios para permitir otro reporte
        self.product_id = False
        self.location_id = False
        self.start_date = False
        self.end_date = fields.Date.today()

        return {
            'name': _('Trazabilidad'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'excel.export.wizard',
            'res_id': self.id,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context':{'active_ids': self.id, 'active_id': self.id}
        }