# ShopEase

A functional Django e-commerce starter with authentication, product browsing and filtering, shopping cart, wishlist, cash-on-delivery checkout, order history, stock control, and Django Admin management.

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install django pillow
python manage.py makemigrations
python manage.py migrate
python manage.py seed_store
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and visit http://127.0.0.1:8000/admin/ to manage products, categories, orders, inventory and customers.

## Notes

- SQLite is used in development (`db.sqlite3`).
- Product records can use an uploaded image or the optional image URL field. The seed command uses remote placeholder imagery.
- Set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=0` before deploying. The bundled key is only for local development.
- The payment choice is deliberately Cash on Delivery; no payment credentials are collected or stored.

## Deploy on Render

This repository includes `render.yaml`, which provisions a Render web service and PostgreSQL database.

1. Push this project to a GitHub repository.
2. In Render, select **New > Blueprint** and connect that GitHub repository.
3. Review the generated `shopease` web service and `shopease-db` PostgreSQL database, then click **Apply**.
4. Once deployment finishes, open the generated `.onrender.com` URL. In the Render Shell, run `python manage.py createsuperuser` and `python manage.py seed_store`.

The free service is for demonstration only. It spins down after inactivity, and the free PostgreSQL database expires after 30 days. Upgrade both services before accepting real customer data.
