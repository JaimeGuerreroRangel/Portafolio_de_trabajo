# -*- encoding: utf-8 -*-

{
    "name": "Extensión de un módulo personalizado sobre el módulo de Contado Riguroso",
    "version": "12.0",
    "depends": ["base", "account"],
    "author": "Jaime Guerrero Rangel",
    "category": "Accounting",
    "description": """ 
        Este módulo extiende otro módulo que ocupaban varias empresas no desarrollado por mí.
        Pero una empresa requería cambios para que se ajustara a sus necesidades, por lo que se creó este módulo.
        * Por cuestiones de privacidad no puedo compartir imagenes del funcionamiento del módulo. Ya que contiene información de la empresa.

            - Se crea la factura de la venta completa al confirmar venta aunque este en pendiente de pago
            - Se Libera una venta pendiente de pago si la factura es pagada al 50% o mas.
            
            * Se agregan los siguientes cambios:
                - Se agrega un nuevo permiso para confirmar "Anticipos" sin tener ventas relacionadas.
                - Se agrega un nuevo ajuste para el tipo de relación de los anticipos. Tomé solo los anticipos que estén relacionados con la venta.
                
            * Se agregan el siguiente cambio en facturas:
                - Al tener el tipo de relación "Anticipo" y tengas el ajuste activado, el botón de "Agregar documento relacionado" solo te permitirá seleccionar anticipos relacionados con la venta actual.
                
            * En los anticipos se hacen los siguientes cambios:
                - Se agrega un nuevo campo que te permite seleccionar ventas que estén en estado "Pendiente de pago y confirmardo" para relacionarlas con el anticipo.
                - Se muestra el historial de cambios del campo "Ventas relacionadas con este anticipo".
                - Se agrega un filtro para mostrar solo los anticipos que estén relacionados con ventas.
                
            * En las ordenes de venta se hacen los siguientes cambios:
                - Se agrega un campo con los anticipos relacionados con la venta.
                - Se modifica la acción planificada de "Ventas pediente de pago" para que no cancelé la venta si tiene anticipos relacionados.
        """,
    "data" : [
        "security/groups.xml",
        "views/account_payment.xml",
        "views/sale_view.xml",
        "views/res_config_settings.xml",
        ],
    "demo": [],
    "images": [],
    "test": [],
    "installable": True,
    "active": False,
    "certificate": False,
}