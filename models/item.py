from utils.db import get_db

CATEGORIES = [
    {'key': 'Books', 'label': 'Books & Study Materials', 'icon': 'fa-book'},
    {'key': 'Electronics', 'label': 'Electronics & Gadgets', 'icon': 'fa-laptop', 'subcategories': ['Phones', 'Tablets', 'Laptops', 'Audio/Headphones', 'Smartwatches', 'Calculators', 'PC Components', 'Chargers & Cables']},
    {'key': 'Gaming', 'label': 'Gaming', 'icon': 'fa-gamepad'},
    {'key': 'Other', 'label': 'Other', 'icon': 'fa-box-open', 'subcategories': ['Sports & Fitness', 'Cloths or Uniform', 'Art & Stationery', 'Bags & Luggage']},
]


class Item:
    @staticmethod
    def create(title, description, price, owner_id, image_paths=None, category='Other'):
        db = get_db()
        cursor = db.execute(
            "INSERT INTO items (title, description, price, owner_id, category) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (title, description, price, owner_id, category),
        )
        row = cursor.fetchone()
        item_id = row['id'] if row else None
        
        if item_id and image_paths:
            for path in image_paths:
                db.execute("INSERT INTO item_images (item_id, image_path) VALUES (%s, %s)", (item_id, path))
        
        db.commit()
        return item_id

    @staticmethod
    def update(item_id, title, description, price, category=None):
        db = get_db()
        if category:
            db.execute(
                "UPDATE items SET title = %s, description = %s, price = %s, category = %s WHERE id = %s",
                (title, description, price, category, item_id),
            )
        else:
            db.execute(
                "UPDATE items SET title = %s, description = %s, price = %s WHERE id = %s",
                (title, description, price, item_id),
            )
        db.commit()

    @staticmethod
    def delete(item_id):
        db = get_db()
        # Resolve and disassociate any reports before item deletion to avoid FK violations.
        db.execute(
            "UPDATE reports SET reported_item_id = NULL, status = 'resolved' WHERE reported_item_id = %s",
            (item_id,),
        )
        db.execute("DELETE FROM item_images WHERE item_id = %s", (item_id,))
        db.execute("DELETE FROM wishlist WHERE item_id = %s", (item_id,))
        db.execute("DELETE FROM items WHERE id = %s", (item_id,))
        db.commit()

    @staticmethod
    def get(item_id):
        db = get_db()
        row = db.execute(
            "SELECT items.*, users.username AS owner_name, users.phone_number AS owner_phone FROM items "
            "JOIN users ON items.owner_id = users.id "
            "WHERE items.id = %s",
            (item_id,),
        ).fetchone()
        
        if row:
            item_dict = dict(row)
            images = db.execute("SELECT image_path FROM item_images WHERE item_id = %s ORDER BY id ASC", (item_id,)).fetchall()
            item_dict['images'] = [img['image_path'] for img in images]
            return item_dict
        return None

    @staticmethod
    def list_all(category=None, min_price=None, max_price=None, sort='newest', search=None):
        db = get_db()
        conditions = ["items.status = 'available'"]
        params = []

        # Category mapping for new hierarchy
        if category and category != 'All':
            # Identify if it's a parent category
            parent_to_subs = {
                'Electronics': ['Electronics', 'Phones', 'Tablets', 'Laptops', 'Audio/Headphones', 'Smartwatches', 'Calculators', 'PC Components', 'Chargers & Cables'],
                'Other': ['Other', 'Sports & Fitness', 'Sports', 'Cloths or Uniform', 'Clothing', 'Art & Stationery', 'Art', 'Bags & Luggage', 'Bags']
            }
            
            if category in parent_to_subs:
                # Search all items in this parent category OR its subcategories
                placeholders = ', '.join(['%s'] * len(parent_to_subs[category]))
                conditions.append(f"items.category IN ({placeholders})")
                params.extend(parent_to_subs[category])
            else:
                # It's an explicit subcategory search. Map legacy names to new ones if applicable
                alias_map = {
                    'Laptops': ['Laptops', 'Electronics'], # Some older items might just be 'Electronics'
                    'Tablets': ['Tablets', 'Phones'], # Legacy fallback
                    'Sports & Fitness': ['Sports & Fitness', 'Sports'],
                    'Cloths or Uniform': ['Cloths or Uniform', 'Clothing'],
                    'Art & Stationery': ['Art & Stationery', 'Art'],
                    'Bags & Luggage': ['Bags & Luggage', 'Bags'],
                }
                cats_to_search = alias_map.get(category, [category])
                placeholders = ', '.join(['%s'] * len(cats_to_search))
                conditions.append(f"items.category IN ({placeholders})")
                params.extend(cats_to_search)

        if min_price is not None:
            conditions.append("items.price >= %s")
            params.append(min_price)

        if max_price is not None:
            conditions.append("items.price <= %s")
            params.append(max_price)

        if search:
            pattern = f"%{search}%"
            conditions.append("(items.title ILIKE %s OR items.description ILIKE %s OR users.username ILIKE %s)")
            params.extend([pattern, pattern, pattern])

        where = " AND ".join(conditions)

        sort_map = {
            'newest': 'items.created_at DESC',
            'oldest': 'items.created_at ASC',
            'price_low': 'items.price ASC',
            'price_high': 'items.price DESC',
        }
        order = sort_map.get(sort, 'items.created_at DESC')

        sql = (
            "SELECT items.*, users.username AS owner_name, users.phone_number AS owner_phone, "
            "(SELECT image_path FROM item_images WHERE item_id = items.id ORDER BY id ASC LIMIT 1) AS image_path "
            "FROM items "
            "JOIN users ON items.owner_id = users.id "
            f"WHERE {where} "
            f"ORDER BY {order}"
        )
        rows = db.execute(sql, tuple(params)).fetchall()
        return rows

    @staticmethod
    def list_all_admin():
        """Return ALL items regardless of status, for admin view."""
        db = get_db()
        rows = db.execute(
            "SELECT items.*, users.username AS owner_name, users.phone_number AS owner_phone, "
            "(SELECT image_path FROM item_images WHERE item_id = items.id ORDER BY id ASC LIMIT 1) AS image_path "
            "FROM items "
            "JOIN users ON items.owner_id = users.id "
            "ORDER BY items.created_at DESC"
        ).fetchall()
        return rows

    @staticmethod
    def flag_item(item_id):
        db = get_db()
        db.execute("UPDATE items SET status = 'flagged' WHERE id = %s", (item_id,))
        db.commit()

    @staticmethod
    def mark_sold_admin(item_id):
        db = get_db()
        db.execute("UPDATE items SET status = 'sold' WHERE id = %s", (item_id,))
        db.commit()

    @staticmethod
    def get_stats():
        db = get_db()
        total = db.execute("SELECT COUNT(*) AS c FROM items").fetchone()['c']
        active = db.execute("SELECT COUNT(*) AS c FROM items WHERE status = 'available'").fetchone()['c']
        sold = db.execute("SELECT COUNT(*) AS c FROM items WHERE status = 'sold'").fetchone()['c']
        flagged = db.execute("SELECT COUNT(*) AS c FROM items WHERE status = 'flagged'").fetchone()['c']
        return {'total': total, 'active': active, 'sold': sold, 'flagged': flagged}

    @staticmethod
    def search(term):
        """Legacy search — now delegates to list_all with search param."""
        return Item.list_all(search=term)

    @staticmethod
    def get_category_counts():
        """Return count of available items per parent category."""
        db = get_db()
        rows = db.execute(
            "SELECT category, COUNT(*) AS cnt FROM items "
            "WHERE status = 'available' GROUP BY category ORDER BY cnt DESC"
        ).fetchall()
        
        # Map old categories and all subcategories to their parent categories
        category_map = {
            'Clothing': 'Other', 'Cloths or Uniform': 'Other',
            'Sports': 'Other', 'Sports & Fitness': 'Other',
            'Art': 'Other', 'Art & Stationery': 'Other',
            'Bags': 'Other', 'Bags & Luggage': 'Other',
            'Phones': 'Electronics', 'Tablets': 'Electronics',
            'Laptops': 'Electronics', 'Audio/Headphones': 'Electronics',
            'Smartwatches': 'Electronics', 'Calculators': 'Electronics',
            'PC Components': 'Electronics', 'Chargers & Cables': 'Electronics',
        }
        
        # Aggregate counts by parent category
        counts = {}
        for row in rows:
            cat = row['category']
            parent_cat = category_map.get(cat, cat)
            counts[parent_cat] = counts.get(parent_cat, 0) + row['cnt']
        
        return counts

    @staticmethod
    def list_by_owner(owner_id):
        db = get_db()
        rows = db.execute(
            "SELECT items.*, "
            "(SELECT image_path FROM item_images WHERE item_id = items.id ORDER BY id ASC LIMIT 1) AS image_path "
            "FROM items WHERE owner_id = %s ORDER BY created_at DESC",
            (owner_id,),
        ).fetchall()
        return rows

    @staticmethod
    def mark_sold(item_id, buyer_id):
        db = get_db()
        db.execute("UPDATE items SET status = 'sold', buyer_id = %s WHERE id = %s", (buyer_id, item_id))
        db.commit()

    @staticmethod
    def list_purchased(buyer_id):
        db = get_db()
        rows = db.execute(
            "SELECT items.*, users.username AS owner_name, users.phone_number AS owner_phone, "
            "(SELECT image_path FROM item_images WHERE item_id = items.id ORDER BY id ASC LIMIT 1) AS image_path "
            "FROM items "
            "JOIN users ON items.owner_id = users.id "
            "WHERE items.buyer_id = %s ORDER BY items.created_at DESC",
            (buyer_id,),
        ).fetchall()
        return rows
