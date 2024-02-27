# -*- encoding: utf-8 -*-

{
    'name' : 'Filtro de pedidos de PdV',
    'version' : '0.1',
    'author' : 'Jaime Guerrero Rangel',
    'license': 'GPL-3',
    'category' : 'Point of Sale',
    'description': """
           * Añade un permiso en los usuarios que activa un filtro para que solo se muestren los pedidos de los ultimos 30 dias.
    """,
    'data':[
        'security/groups.xml',
        'views/pos_order_view.xml',
    ],
    'depends': ['base','point_of_sale','experts_groups'],
    'installable': True,
}
