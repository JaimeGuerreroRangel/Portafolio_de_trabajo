# -*- coding: utf-8 -*-

{
    "name": "Personalización de reportes de Inventario",
    "version": "17.1",
    "author": "Jaime Guerrero Rangel",
    "category": "Stock/Reports",
    "description": """
        * Este módulo personaliza reportes que pertencen a ventas:
            - Se personaliza el reporte de Operaciones de recolección, Recibo de entrega:
    """,
    "license" : "AGPL-3",
    "depends": ['base', 'stock', 'product', 'digest'],
    "data": [
        'reports/stock_reports_view.xml',
        'reports/stock_picking_pdf.xml',
        'reports/stock_delivery.xml',
        'views/stock_picking_view.xml',
             ],
    "installable" : True,
    "active" : False,
}