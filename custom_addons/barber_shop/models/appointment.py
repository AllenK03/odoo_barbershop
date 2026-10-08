# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class BarberAppointment(models.Model):
    _name = "barber.appointment"
    _description = "Cita / Orden de Atención"
    _order = "date_start desc, id desc"

    name = fields.Char(
        string="Código de Cita",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("Nuevo"),
    )
    customer_id = fields.Many2one("res.partner", string="Cliente", required=True)
    barber_id = fields.Many2one(
        "barber.barber", string="Barbero / Estilista", required=True
    )
    date_start = fields.Datetime(
        string="Fecha y Hora de Inicio", default=fields.Datetime.now, required=True
    )
    date_end = fields.Datetime(string="Fecha y Hora Fin")
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("confirmed", "Confirmada"),
            ("in_progress", "En Atención"),
            ("done", "Finalizada"),
            ("cancel", "Cancelada"),
        ],
        string="Estado",
        default="draft",
        required=True,
        tracking=True,
    )

    # Relaciones de Servicios y Productos
    service_ids = fields.Many2many("barber.service", string="Servicios Solicitados")
    product_line_ids = fields.One2many(
        "barber.appointment.line", "appointment_id", string="Productos Retail"
    )

    # Moneda y Totales Financieros
    currency_id = fields.Many2one(
        "res.currency",
        string="Moneda",
        default=lambda self: self.env.company.currency_id,
    )
    total_services = fields.Monetary(
        string="Total Servicios",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_products = fields.Monetary(
        string="Total Productos",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    total_amount = fields.Monetary(
        string="Monto Total",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    # Motor Dual de Comisiones y Margen Local
    barber_commission = fields.Monetary(
        string="Comisión Barbero",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )
    shop_profit = fields.Monetary(
        string="Ganancia Local",
        compute="_compute_totals",
        store=True,
        currency_field="currency_id",
    )

    # Integraciones de Inventario y Facturación
    picking_id = fields.Many2one(
        "stock.picking", string="Albarán de Inventario", copy=False, readonly=True
    )
    invoice_id = fields.Many2one(
        "account.move", string="Factura", copy=False, readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("Nuevo")) == _("Nuevo"):
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "barber.appointment"
                ) or _("Nuevo")
        return super(BarberAppointment, self).create(vals_list)

    @api.depends("service_ids", "product_line_ids.subtotal", "barber_id")
    def _compute_totals(self):
        for app in self:
            # 1. Total Servicios
            t_services = sum(app.service_ids.mapped("price"))
            app.total_services = t_services

            # 2. Total Productos Retail
            t_products = sum(app.product_line_ids.mapped("subtotal"))
            app.total_products = t_products

            # 3. Monto Total
            t_amount = t_services + t_products
            app.total_amount = t_amount

            # 4. Cálculo Dual de Comisiones
            barber_comm = 0.0
            if app.barber_id:
                for service in app.service_ids:
                    rate = (
                        service.custom_commission
                        if service.custom_commission > 0
                        else app.barber_id.service_commission_rate
                    )
                    barber_comm += service.price * (rate / 100.0)

                barber_comm += t_products * (
                    app.barber_id.product_commission_rate / 100.0
                )

            app.barber_commission = barber_comm
            app.shop_profit = t_amount - barber_comm

    # Botones de Flujo de Trabajo
    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_start(self):
        self.write({"state": "in_progress"})

    def action_done(self):
        for app in self:
            if app.product_line_ids:
                app._create_and_validate_stock_picking()
        self.write({"state": "done", "date_end": fields.Datetime.now()})

    def action_cancel(self):
        self.write({"state": "cancel"})

    def action_draft(self):
        self.write({"state": "draft"})

    # --- LÓGICA DE INVENTARIO (STOCK) ---
    def _create_and_validate_stock_picking(self):
        self.ensure_one()
        picking_type = self.env["stock.picking.type"].search(
            [
                ("code", "=", "outgoing"),
                ("warehouse_id.company_id", "=", self.env.company.id),
            ],
            limit=1,
        )

        if not picking_type:
            raise UserError(
                _(
                    "No se encontró un tipo de operación de salida de inventario para la compañía actual."
                )
            )

        for line in self.product_line_ids:
            if line.product_id.type == "product":
                if line.product_id.qty_available < line.qty:
                    raise UserError(
                        _(
                            "Stock insuficiente para el producto '%s'.\n"
                            "Disponible: %s | Solicitado en Cita: %s"
                        )
                        % (
                            line.product_id.display_name,
                            line.product_id.qty_available,
                            line.qty,
                        )
                    )

        location_id = picking_type.default_location_src_id.id
        customer_loc = (
            self.customer_id.property_stock_customer.id
            or self.env.ref("stock.stock_location_customers").id
        )

        picking_vals = {
            "partner_id": self.customer_id.id,
            "picking_type_id": picking_type.id,
            "location_id": location_id,
            "location_dest_id": customer_loc,
            "origin": self.name,
            "move_ids_without_package": [
                (
                    0,
                    0,
                    {
                        "name": line.product_id.display_name,
                        "product_id": line.product_id.id,
                        "product_uom_qty": line.qty,
                        "product_uom": line.product_id.uom_id.id,
                        "location_id": location_id,
                        "location_dest_id": customer_loc,
                    },
                )
                for line in self.product_line_ids
            ],
        }

        picking = self.env["stock.picking"].create(picking_vals)
        picking.action_confirm()
        picking.action_assign()

        for move in picking.move_ids:
            move.quantity = move.product_uom_qty

        picking.button_validate()
        self.picking_id = picking.id

    def action_view_picking(self):
        self.ensure_one()
        if not self.picking_id:
            raise UserError(
                _("No hay ningún albarán de inventario asociado a esta cita.")
            )
        return {
            "name": _("Albarán de Inventario"),
            "type": "ir.actions.act_window",
            "res_model": "stock.picking",
            "res_id": self.picking_id.id,
            "view_mode": "form",
        }

    # --- LÓGICA DE FACTURACIÓN UNIFICADA (ACCOUNT.MOVE) ---
    def action_create_invoice(self):
        """Genera una factura borrador unificando servicios y productos retail"""
        self.ensure_one()
        if self.invoice_id:
            raise UserError(_("Ya existe una factura asociada a esta cita."))

        journal = self.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)], limit=1
        )

        if not journal:
            raise UserError(
                _(
                    "No se encontró un Diario de Ventas (tipo sale) configurado en la compañía."
                )
            )

        invoice_lines = []

        # 1. Agregar líneas de Servicios
        for service in self.service_ids:
            invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "name": _("Servicio: %s") % service.name,
                        "quantity": 1.0,
                        "price_unit": service.price,
                    },
                )
            )

        # 2. Agregar líneas de Productos Retail
        for line in self.product_line_ids:
            invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": line.product_id.id,
                        "name": line.product_id.display_name,
                        "quantity": line.qty,
                        "price_unit": line.price_unit,
                    },
                )
            )

        if not invoice_lines:
            raise UserError(
                _("No se puede generar factura sin servicios ni productos registrados.")
            )

        invoice_vals = {
            "move_type": "out_invoice",
            "partner_id": self.customer_id.id,
            "journal_id": journal.id,
            "invoice_date": fields.Date.context_today(self),
            "invoice_origin": self.name,  # Se corrigió de 'origin' a 'invoice_origin'
            "invoice_line_ids": invoice_lines,
        }

        invoice = self.env["account.move"].create(invoice_vals)
        self.invoice_id = invoice.id

        return self.action_view_invoice()

    def action_view_invoice(self):
        self.ensure_one()
        if not self.invoice_id:
            raise UserError(_("No hay ninguna factura asociada a esta cita."))
        return {
            "name": _("Factura de Cliente"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "res_id": self.invoice_id.id,
            "view_mode": "form",
        }
