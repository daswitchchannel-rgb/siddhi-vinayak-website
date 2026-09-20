# V7 Production deployment checklist

This package is deployment-ready as a Flask/Gunicorn container, but it is **not cloud-hosted by this chat**.

## Recommended deployment shape
Internet/HTTPS
→ reverse proxy / platform
→ Gunicorn
→ Flask API
→ persistent SQLite volume (or migrate to PostgreSQL)
→ persistent media volume/object storage

## Before public launch
1. Set a strong `ADMIN_PASSWORD`.
2. Set a random `SECRET_KEY`.
3. Use HTTPS.
4. Restrict upload size/type further if needed.
5. Move media to object storage/CDN for scale.
6. Back up the database.
7. Replace SQLite with PostgreSQL when multiple concurrent admins/orders are expected.
8. Add rate limiting and CSRF protection to the admin/auth layer.
9. Add payment-provider webhooks only after the merchant account is configured.
10. Never commit `.env` secrets.

## API
GET /api/health
GET /api/data
POST /api/login
POST /api/logout
POST /api/inquiries
POST /api/upload
POST /api/materials
POST /api/designs
POST /api/products


## Render Free setup

This repository includes `render.yaml` for Render Blueprint deployment. Render supports free Python web services, but its free filesystem is ephemeral: uploaded media and SQLite data can be lost on restart/redeploy/spin-down. For a real business site, use persistent Postgres/object storage when those are available.
