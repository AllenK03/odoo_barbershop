# Barber Shop Management System (barber_shop)

Custom module developed on Odoo 17 Community Edition designed for the operational, financial, and inventory management of barber shops and aesthetic salons. It manages appointment scheduling, barber commission tracking, retail product sales, automatic stock deductions, unified invoicing, and printable PDF tickets.

## 🚀 Key Features

* **Barber & Stylist Management:** Personal records (ID/DNI, contact info), system user linking, and customizable dual commission schemes (Services % and Retail Products %).
* **Service Catalog:** Registry of services (haircuts, beard trimming, treatments) with pricing, duration in minutes, and service-specific custom commission overrides.
* **Appointment Scheduling & Lifecycle (`barber.appointment`):**
  * Automatic sequence generation (`CITA/YYYY/00001`).
  * Workflow tracking: *Draft*, *Confirmed*, *In Progress*, *Done*, and *Cancelled*.
  * Multi-view visualization: Kanban Board (grouped by status), Weekly Calendar, List (Tree), and Form.
* **Dual Commission & Profit Engine:** Real-time computation of barber earnings and net shop profit for both services rendered and retail items sold.
* **Automated Stock Integration (`stock.picking`):** Real-time stock validation and automatic Delivery Order creation and validation upon appointment completion.
* **Unified Invoicing (`account.move`):** One-click draft customer invoice generation consolidating services and retail products into a single document.
* **QWeb PDF Ticket Report:** Printable customer appointment and consumption receipts with itemized breakdown.

## 🛠️ Tech Stack

* **ERP:** Odoo 17.0 (Community Edition)
* **Database:** PostgreSQL 15
* **Containerization:** Docker & Docker Compose
* **PDF Engine:** Wkhtmltopdf
* **Languages:** Python 3.10+, XML, QWeb, JS (OWL Framework)

## 📂 Project Structure

```plaintext
odoo_barbershop/
├── docker-compose.yml          # Container environment configuration (Odoo + PostgreSQL)
├── .gitignore                  # Git exclusions
├── README.md                   # Project documentation
└── custom_addons/
    └── barber_shop/            # Custom module
        ├── __manifest__.py     # Module manifest
        ├── security/           # Access rules (ir.model.access.csv)
        ├── data/               # Automatic sequences (ir_sequence_data.xml)
        ├── models/             # Python data logic & computations
        ├── views/              # XML views (Form, Tree, Kanban, Calendar, Menus)
        └── reports/            # QWeb PDF print templates (Appointment Ticket)
```

⚙ Prerequisites
Ensure you have the following installed on your host machine:

Docker Desktop (or Docker Engine + Docker Compose)

Git

📦 Local Installation & Deployment
Clone the repository:

Bash
git clone [https://github.com/giordanocarmine/odoo_barbershop.git](https://github.com/giordanocarmine/odoo_barbershop.git)
cd odoo_barbershop
Start services with Docker Compose:

Bash
docker compose up -d
Install / Sync the module in the database (barbershop_db):

Bash
docker compose exec web odoo --db_host=db -r odoo -w odoo -i barber_shop -d barbershop_db --stop-after-init
Restart the Odoo web service:

Bash
docker compose restart web
Access the application:
Open your browser and navigate to http://localhost:8069 (Default credentials: admin / admin).

⚙️ Recommended Initial Setup
When deploying to a new environment for the first time:

Company Profile: Update your business name, address, phone, and logo under Settings > Companies.

Sales Journal: Verify under Invoicing > Configuration > Journals that a journal with type Sales (sale) exists to enable invoice generation.

Retail Products: Ensure that retail products have the Can be Sold flag enabled and available stock under Inventory to enable automated delivery orders.

👤 Author
Diego Giordano - Lead Developer - GitHub

📜 License
This project is licensed under LGPL-3.0. See the manifest file for details.

