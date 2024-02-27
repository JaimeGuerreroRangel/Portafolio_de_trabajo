# -*- encoding: utf-8 -*-

from odoo import api, fields, models, _, tools, SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import timedelta

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        """Modificamos la busqueda de pedidos para que solo se muestren los pedidos de los ultimos 30 dias si el usuario tiene el permiso correspondiente."""
        # Aseguramos que args no sea None
        args = args or []
        # Verificamos si el usuario tiene el permiso de solo ver los pedidos de los ultimos 30 dias
        if self.env.context.get('default_filter_30_days') and self.env.user.has_group('glazier_pos_extend.group_pos_30_days_only'):
            # Realizamos la busqueda de los pedidos de los ultimos 30 dias
                today = fields.Date.context_today(self)
                date_limit = today - timedelta(days=30)
                args += [('create_date', '>=', date_limit)]
        return super(PosOrder, self).search(args, offset, limit, order, count)