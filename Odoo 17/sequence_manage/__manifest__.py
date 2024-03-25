# -*- encoding: utf-8 -*-

{
    "name": "Sequencias independientes",
    "version": "17.1",
    "depends": ["base","sale_stock", "purchase_stock"],
    "author": "Jaime Guerrero Rangel",
    "category": "Other Modules",
    "license" : "AGPL-3",
    "description": """
        * Este módulo permite tener secuencias independientes para:
            - Cotizaciones y ordenes de venta
            - Cotizaciones y ordenes de compra
            
        * Se añade el campo "Cotización Origen" en las ordenes de compra y venta para poder identificar la cotización de origen.
        * Se añade el campo "Cotización Origen" en los reportes de ordenes de compra y venta.
        * Se añade el campo "Cotización Origen" en los pickings para poder identificar la cotización de origen.
    """,
    "data" : [
        'data/ir_sequence_data.xml',
        'reports/sale_report_pdf.xml',
        'reports/purchase_report.xml',
        'views/sale_order_view.xml',
        'views/purchase_order_view.xml',
        'views/stock_view.xml',
        ],
    "installable": True,
    "active": False,
    "certificate": False,
}