# -*- encoding: utf-8 -*-

{
    "name": "Validaciones de almacén por usuario",
    "version": "0.1",
    "author" : "Jaime Guerrero Rangel",
    "category" : 'Stock',
    "license" : "AGPL-3",
    "description": """
        * Este módulo permite validar movimientos de almacén ponderando los almacenes permitidos por usuario.
    """,
    "depends": ["base", "stock", 'sale_stock','purchase_stock'],
    "data": ["views/user_view.xml",
             ],
    "installable" : True,
    "active" : False,
}