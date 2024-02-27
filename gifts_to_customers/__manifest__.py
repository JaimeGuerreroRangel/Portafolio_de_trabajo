# -*- encoding: utf-8 -*-

{
    "name": "Regalos a Clientes",
    "version": "0.1",
    "author": "Jaime Guerrero Rangel",
    "category": "Partner",
    "license" : "AGPL-3",
    "Description": """
        * Este módulo sirve para dar regalos a los clientes nuevos al hacer su primera compra.
        
        * El siguiente módulo agrega las siguientes funcionalidades:
            - En la vista formulario de clientes:
                - Agregar un campo booleano en el formulario de clientes para indicar si ya recibió su regalo.
                - Al instalar el módulo, se actualiza el campo booleano en todos los clientes existentes para que no se les vuelva a entregar el regalo.
                - A los nuevos clientes creados pueden recibir su regalo.
            - En configuración de la compañía:
                - Se agrega una nueva configuración para indicar si la compañía da regalos a sus clientes se encuentra en Ajustes/Ventas/Catálogo de productos.
            - En el formulario de productos:
                - Se agrega un campo booleano para indicar si el producto es un regalo o el producto da un regalo.
    """,
    "depends": ["base", "sale", "stock", "product"],
    "data": [
        "data/res_partner_data.xml",
        "views/product_template_view.xml",
        "views/res_config_settings.xml",
        "views/res_partner_view.xml",
        "views/sale_order_view.xml",
             ],
    "demo": [],
    "images": [],
    "test": [],
    "installable": True,
    "active": False,
    "certificate": False,
}