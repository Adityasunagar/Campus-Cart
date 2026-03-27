# Campus Cart - Enhanced Student Marketplace

A modern, feature-rich Flask-based marketplace for campus students to buy and sell items securely.

##  New Features & Improvements

### 1. **Online Payment Integration** 
- **Stripe Payment Gateway Integration**
  - Secure card payments (Debit, Credit, Digital Wallets)
  - Checkout page with order summary
  - Payment confirmation and tracking
  - Automatic transaction recording
  - Future support for UPI and local payment methods

### 2. **Seller-Buyer Interaction System** 
- **Transactions & Orders Management**
  - Order history for both buyers and sellers
  - Transaction tracking with status (pending, completed)
  - Seller contact information displayed on product listings
  - Direct messaging between buyers and sellers

### 3. **Ratings & Reviews System** 
- **User Rating System**
  - Rate sellers after purchase (1-5 stars)
  - Add optional comments/feedback
  - View average ratings and reviewed feedback
  - Build trust in the community

### 4. **Seller Contact Information** 
- **Contact Details on Listings**
  - Sellers add contact number while listing items
  - Buyers see contact info before purchase
  - WhatsApp/phone contact for direct communication
  - Both pre and post-purchase communication options

### 5. **Smart Category Filtering** 
- **Dynamic Category Display**
  - Only shows categories with available products
  - Real-time product count per category
  - Filter items by category with visual badges
  - Categories automatically appear/disappear based on products

### 6. **Modern UI with Bootstrap 5** 
- **Responsive Design**
  - Bootstrap 5 framework integration
  - Custom CSS for each page type
  - Mobile-friendly layouts
  - Improved navigation with dropdown menus
  - Enhanced forms and buttons

### 7. **Improved User Experience** 
- **Better Navigation**
  - Dropdown profile menu
  - Quick access to Orders and Sales
  - Clear status indicators
  - Enhanced feedback messages

- **Order Management Pages**
  - My Orders - View all purchases
  - My Sales - View all sales
  - Transaction history
  - Rating system integration

## 📋 Database Schema Updates

### New Tables

```sql
-- Transactions table for payment tracking
CREATE TABLE transactions (
  id SERIAL PRIMARY KEY,
  item_id INTEGER NOT NULL REFERENCES items(id),
  buyer_id INTEGER NOT NULL REFERENCES users(id),
  seller_id INTEGER NOT NULL REFERENCES users(id),
  amount DECIMAL(10, 2) NOT NULL,
  stripe_payment_id VARCHAR(255),
  status VARCHAR(20),
  payment_method VARCHAR(50),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

-- Ratings table for reviews
CREATE TABLE ratings (
  id SERIAL PRIMARY KEY,
  transaction_id INTEGER NOT NULL REFERENCES transactions(id),
  rater_id INTEGER NOT NULL REFERENCES users(id),
  rated_user_id INTEGER NOT NULL REFERENCES users(id),
  rating INT,
  comment TEXT,
  created_at TIMESTAMP
);
```

### Updated Items Table

```sql
ALTER TABLE items ADD COLUMN contact_number VARCHAR(20);
```

##  Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL
- FFmpeg (optional, for media handling)

### Step 1: Clone & Install Dependencies

```bash
cd f:\ADITYA\CampusCart
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file from `.env.example`:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your configuration
```

**Required configurations:**
```
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=campuscart

STRIPE_PUBLIC_KEY=pk_test_your_key
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_KEY=whsec_your_key

SECRET_KEY=your-secret-key
```

### Step 3: Get Stripe Keys

1. Create account at [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to "Developers" > "API Keys"
3. Copy the **Public Key** and **Secret Key**
4. Add them to your `.env` file

### Step 4: Setup Database

```bash
# Run migrations
python migrate.py

# Verify database schema
# Should see no errors
```

### Step 5: Run Application

```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

##  Project Structure

```
CampusCart/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── migrate.py            # Database migrations
├── requirements.txt      # Python dependencies
│
├── models/
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── item.py          # Product/Item model
│   ├── message.py       # Chat messages
│   ├── transaction.py   # NEW: Payments & Ratings
│   ├── wishlist.py      # Wishlist model
│   └── report.py        # Report/Flag items
│
├── routes/
│   ├── __init__.py
│   ├── auth.py          # Authentication
│   ├── items.py         # Product listing
│   ├── chat.py          # Messaging
│   ├── payment.py       # NEW: Payment & Orders
│   ├── profile.py       # User profile
│   └── admin.py         # Admin panel
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   ├── responsive.css
│   │   └── bootstrap-custom.css  # NEW: Bootstrap customizations
│   ├── js/
│   │   ├── main.js      # UPDATED: Interactive features
│   │   ├── chat.js
│   │   └── items.js
│   ├── images/
│   └── uploads/         # User uploaded images
│
├── template/
│   ├── base.html        # Base template with Bootstrap
│   ├── index.html       # Home/Browse
│   ├── add.html         # UPDATED: Add contact_number
│   ├── detail.html      # UPDATED: Payment button & contact
│   ├── checkout.html    # NEW: Payment checkout
│   ├── orders.html      # NEW: Purchase history
│   ├── sales.html       # NEW: Sales history
│   ├── login.html
│   ├── register.html
│   ├── profile.html
│   ├── chat.html
│   └── admin.html
│
├── utils/
│   ├── db.py           # Database connection
│   └── helpers.py      # Utility functions
│
└── .env.example        # Environment variables template
```

##  API Endpoints

### New Payment Routes

```
GET/POST  /payment/checkout/<item_id>    - Payment checkout page
GET       /payment/success                - Payment success handler
GET       /payment/orders                 - View purchases
GET       /payment/sales                  - View sales
POST      /payment/rate/<transaction_id>  - Submit rating
POST      /payment/webhook                - Stripe webhook
```

##  Security Features

- ✅ Secure password hashing (Werkzeug)
- ✅ Session-based authentication
- ✅ CSRF protection via Flask
- ✅ Stripe PCI compliance (no card data storage)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Content moderation (banned keywords filter)
- ✅ Admin moderation tools

##  User Workflows

### For Buyers

1. **Browse Products**
   - View all items or filter by category
   - Search functionality
   - Price range filtering
   - Sort by newest, price, etc.

2. **Purchase Item**
   - See seller's contact number
   - Message seller before purchase
   - Add to wishlist
   - Proceed to payment (Stripe)

3. **Post-Purchase**
   - View in "My Orders"
   - Contact seller via chat
   - Rate seller (1-5 stars)
   - View transaction history

### For Sellers

1. **List Items**
   - Upload product images (camera or file)
   - Add description, price, category
   - Include contact number
   - Manage listings

2. **Manage Sales**
   - View "My Sales" section
   - See all buyer orders
   - Chat with buyers
   - Track transaction status

3. **Build Reputation**
   - Receive buyer ratings
   - View average rating
   - Read customer feedback

##  Campus-Specific Features

- Student-only marketplace
- Campus community focus
- Trust building through ratings
- Easy item categorization (Books, Electronics, etc.)
- Direct contact information for local meetups

##  Troubleshooting

### Payment Not Working
- Verify Stripe keys in `.env`
- Check if using test keys (pk_test_, sk_test_)
- Ensure webhook endpoint is configured in Stripe dashboard

### Images Not Uploading
- Check `uploads/` folder permissions
- Verify file size (max 10MB recommended)
- Clear browser cache if images don't show

### Database Connection Issues
- Verify PostgreSQL is running
- Check credentials in `.env`
- Run `python migrate.py` again

### Category Not Showing
- Category only appears if it has products
- Add more items to that category
- Page refreshes automatically

##  Documentation

### Adding New Features
1. Update models in `models/`
2. Create routes in `routes/`
3. Create templates in `template/`
4. Add CSS in `static/css/`
5. Update migrations if DB schema changes

### Customizing Styles
- `static/css/style.css` - Global styles
- `static/css/bootstrap-custom.css` - Bootstrap customizations
- `static/css/responsive.css` - Mobile responsive

##  Deployment

For production deployment:

1. Set `DEBUG=False` in config
2. Use strong `SECRET_KEY`
3. Configure PostgreSQL properly
4. Set up Stripe live keys
5. Use HTTPS only
6. Configure environment variables securely

## 📝 License

Campus Cart is open source and available for educational purposes.

##  Contributing

To contribute improvements:
1. Test thoroughly
2. Follow code style
3. Update documentation
4. Submit changes for review

##  Support

For issues or questions:
- Check troubleshooting section
- Review database schema
- Verify configuration
- Check payment integration guide

---

**Last Updated:** March 2026
**Version:** 2.0 (Enhanced with Payments, Ratings & Improved UI)
