# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _ 
from odoo.exceptions import UserError

class ResUsers(models.Model):
    _inherit='res.users'

    # Relación de almacenes permitidos por usuario
    warehouse_ids_validate = fields.Many2many('stock.warehouse','warehouse_user','user_id','warehouse_id','Almacenes', 
                                     help='El usuario que tenga seleccionado un almacén en este campo, solo podrá validar movimientos de almacén que estén relacionados con el almacén seleccionado.')