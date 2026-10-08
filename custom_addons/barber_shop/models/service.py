# -*- coding: utf-8 -*-
from odoo import models, fields


class BarberService(models.Model):
    _name = "barber.service"
    _description = "Servicios de Barbería"

    name = fields.Char(string="Nombre del Servicio", required=True)
    price = fields.Float(string="Precio ($)", required=True, default=0.0)
    duration = fields.Integer(string="Duración (Minutos)", default=30)
    custom_commission = fields.Float(
        string="Comisión Personalizada (%)",
        help="Sobrescribe la comisión base del barbero para este servicio específico (opcional).",
    )
    active = fields.Boolean(string="Activo", default=True)
