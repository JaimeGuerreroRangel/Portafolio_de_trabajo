# -*- encoding: utf-8 -*-

{
    "name": "Reporte de valoración de existencias",
    "version": "0.1",
    "author": "Jaime Guerrero Rangel",
    "category": "Stock/Report",
    "license": "AGPL-3",
    "description": """
        *Se añade reporte de valoración de existencias
    """,
    "depends": ["base", "stock", "stock_account"],
    "data": ["reports/stock_value_view.xml",
             "reports/stock_value_report.xml",],
    "installable": True,
    "active": False,
    "certificate": False,
}