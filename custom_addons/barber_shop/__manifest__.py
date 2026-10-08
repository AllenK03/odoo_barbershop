# -*- coding: utf-8 -*-
{
    "name": "Barber Shop Management",
    "version": "17.0.1.0.0",
    "category": "Services/BarberShop",
    "summary": "Módulo de gestión integral para barberías y salones de estética",
    "description": """
        Módulo vertical para la gestión de barberías:
        - Agendamiento de citas y asignación de estilistas.
        - Catálogo de servicios y venta de productos retail.
        - Control e integración automática con Inventario (Stock Picking).
        - Motor dual de cálculo de comisiones (servicios + productos).
        - Facturación unificada en Odoo.
    """,
    "author": "Diego Giordano",
    "website": "https://github.com/giordanocarmine",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product",
        "stock",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/barber_views.xml",
        "views/service_views.xml",
        "views/appointment_views.xml",
        "views/menus.xml",
        "reports/appointment_ticket_report.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
