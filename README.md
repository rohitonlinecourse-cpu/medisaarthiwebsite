# MediSaarthi Website Starter

A Flask + SQLite starter website styled after the supplied MediSaarthi reference image.

## Included
- Responsive home page matching the green/blue pharmacy style
- Medicine search + demo catalogue
- Cart and order form
- Flat ₹30 delivery charge
- Mobile contact: 7859090242
- Prescription upload field
- Automatic email notification support through SMTP environment variables
- Customer order tracking page: `/track/<order_id>`
- Admin order list/status update page: `/admin`
- WhatsApp ordering button

## Run locally
```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## Email notifications
Copy `.env.example` values into your hosting environment. For Gmail, use an App Password rather than your normal password. Configure SMTP before production.

## Important production work
- Add real licensed-pharmacy inventory and prescription verification.
- Add proper admin login/authentication (the demo `/admin` is intentionally not protected).
- Add HTTPS, secure file storage, input validation, rate limiting and backups.
- Add payment gateway (UPI/card/COD) if required.
- Add SMS/WhatsApp transactional notifications if required.
- Configure domain, hosting and business/legal details.
