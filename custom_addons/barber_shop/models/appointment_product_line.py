# -*- coding: utf-8 -*-
from odoo import models, fields, api


class BarberAppointmentLine(models.Model):
    _name = "barber.appointment.line"
    _description = "Línea de Productos de la Cita"

    appointment_id = fields.Many2one(
        "barber.appointment", string="Cita / Orden", ondelete="cascade"
    )
    product_id = fields.Many2one(
        "product.product",
        string="Producto",
        required=True,
        domain="[('sale_ok', '=', True)]",
    )
    qty = fields.Float(string="Cantidad", default=1.0, required=True)

    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    price_unit = fields.Monetary(
        string="Precio Unitario",
        currency_field="currency_id",
        required=True,
        default=0.0,
    )
    subtotal = fields.Monetary(
        string="Subtotal",
        compute="_compute_subtotal",
        store=True,
        currency_field="currency_id",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price

    @api.depends("qty", "price_unit")
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit
