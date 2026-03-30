# CampusCart - Enhanced Student Marketplace

A modern, feature-rich Flask-based marketplace for campus students to buy/sell safely with admin moderation and real-time chat.

## 🚀 What’s included

- Flask app with blueprints
- Socket.IO chat
- PostgreSQL persistence
- Admin dashboard (manage users/items/reports)
- Report & ban actions
- Item listing + edit + delete
- Wishlist, purchase/mark sold
- `current_user` context processor
- 5000-5100 auto port fallback in `run.py`
- UI polish (glassmorphism + neon)
- Componentized templates (`button_macros`)

---

## ✨ App structure

```
CampusCart/
├── app.py
├── run.py
├── wsgi.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── app/
│   ├── __init__.py
│   ├── extensions.py
│   ├── models/
│   │   ├── user.py
│   │   ├── item.py
│   │   ├── report.py
│   │   ├── message.py
│   │   ├── wishlist.py
│   │   └── transaction.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── items.py
│   │   ├── chat.py
│   │   ├── profile.py
│   │   ├── admin.py
│   │   └── ...
│   └── ...
├── static/
│   ├── css/style.css
│   ├── css/responsive.css
│   ├── js/*.js
│   └── images/
├── template/
│   ├── base.html
│   ├── index.html
│   ├── detail.html
│   ├── auth/*.html
│   ├── components/button_macros.html
│   └── ...
├── utils/
│   ├── db.py
│   └── helpers.py
├── migrations/  (if used)
├── migrate.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔧 Setup

### 1. Prerequisites
- Python 3.8+
- PostgreSQL
- (Optional) FFmpeg for media support

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment

Copy `.env.example` → `.env`:

```bash
cp .env.example .env
```

Update with your values:

```bash
DB_USER=postgres
DB_PASSWORD=xxxx
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campuscart
SECRET_KEY=your-secret
STRIPE_PUBLIC_KEY=xxxx
STRIPE_SECRET_KEY=xxxx
STRIPE_WEBHOOK_KEY=xxxx
```

### 4. Run DB migration

```bash
python migrate.py
```

### 5. Start app

```bash
python app.py
```

or with port fallback:

```bash
python run.py
```

Open `http://localhost:5000` or chosen port.

---

## 🧩 Main features

### User features
- Register/login/logout
- Add/edit/delete item
- Search, filters, sorting
- Wishlist add/remove
- Item detail + chat + contact + buy
- Reports (reason + admin review)

### Admin features
- Admin secret login `/admin/secret-login`
- Users management (promote/demote/ban/delete)
- Item management + flag
- Report handling (resolve/ban/delete)
- Stats dashboard

### Extra features
- Ratings/reviews (planned in schema)
- Stripe-like placeholder payment support
- Real-time chat (Socket.IO)
- Responsive UI
- Componentized template macros

---

## 🗄️ DB schema (key tables)

- users
- items
- item_images
- messages
- wishlist
- reports

Item delete behavior now handles report FK with pre-cleanup:
- `UPDATE reports SET reported_item_id=NULL, status='resolved' WHERE reported_item_id=%s`

---

## 🧪 Tests

```bash
pip install pytest
python -m pytest -q
```

---

## 🛡️ Security

- Password hashing (Werkzeug)
- Session auth
- SQL parameterized queries
- CSRF / best practices
- Admin checks
- Content moderation filters

---

## ✨ Deployment

1. `DEBUG=False`
2. strong `SECRET_KEY`
3. secure DB config
4. Stripe live keys and HTTPS
5. gunicorn (via `wsgi.py`)

---

## 📝 License

Open-source / educational.

---

**Last Updated:** March 2026
**Version:** 2.0 (Enhanced)
