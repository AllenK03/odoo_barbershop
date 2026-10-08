# -*- coding: utf-8 -*-
from odoo import models, fields


class BarberBarber(models.Model):
    _name = "barber.barber"
    _description = "Barbero / Estilista"

    name = fields.Char(string="Nombre del Barbero", required=True)
    identification_id = fields.Char(string="Cédula / DNI")
    user_id = fields.Many2one("res.users", string="Usuario del Sistema")
    phone = fields.Char(string="Teléfono")
    email = fields.Char(string="Correo Electrónico")
    color = fields.Integer(string="Color en Calendario")
    active = fields.Boolean(string="Activo", default=True)

    # Motor de comisiones base (Valores directos de 0 a 100)
    service_commission_rate = fields.Float(
        string="Comisión por Servicios (%)",
        default=50.0,
        help="Porcentaje base de comisión por servicios. Ej: Escriba 50 para el 50%.",
    )
    product_commission_rate = fields.Float(
        string="Comisión por Productos (%)",
        default=10.0,
        help="Porcentaje de comisión por venta de productos retail. Ej: Escriba 10 para el 10%.",
    )
