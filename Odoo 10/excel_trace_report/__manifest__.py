# -*- encoding: utf-8 -*-

{
    'name': 'Reporte de trazabilidad ',
    'version': '10.0',
    'author': 'Jaime Guerrero Rangel',
    'category': 'Excel',
    'description': """
        * Este módulo agrega un reporte de excel sobre movimientos de productos.
            - Selecciona un producto, almacén y fechas para obtener un reporte de excel con los movimientos de ese producto en ese almacén en ese rango de fechas.
            - Muestra todos los movimientos de entrada y salida de ese producto en ese almacén en ese rango de fechas.
            - Muestra la cantidad de productos en stock en ese almacén en ese rango de fechas.
            - Muestra el costo promedio del producto.
            - Si el movimiento tiene una factura o nota de entrega asociada, muestra el número de factura o nota de entrega.
            - Muestra el usuario que realizó el movimiento.
    """,
    'depends': ['base', 'purchase', 'sale', 'stock', 'product'],
    'data': [
        'wizard/wizard_trace_report.xml',
        ],
}