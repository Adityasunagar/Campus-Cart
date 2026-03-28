from werkzeug.security import generate_password_hash, check_password_hash
from utils.db import get_db

class User:
    @staticmethod
    def create(username, email, password, phone_number=None, is_admin=False):
        db = get_db()
        hashed = generate_password_hash(password)
        cursor = db.execute(
            "INSERT INTO users (username, email, password, phone_number, is_admin) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (username, email, hashed, phone_number, 1 if is_admin else 0),
        )
        db.commit()
        row = cursor.fetchone()
        return row['id'] if row else None

    @staticmethod
    def find_by_email(email):
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE email = %s", (email,)).fetchone()
        return row

    @staticmethod
    def find_by_username(username):
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE username = %s", (username,)).fetchone()
        return row

    @staticmethod
    def find_by_id(user_id):
        db = get_db()
        row = db.execute("SELECT * FROM users WHERE id = %s", (user_id,)).fetchone()
        return row

    @staticmethod
    def authenticate(email, password):
        user = User.find_by_email(email)
        if user and check_password_hash(user['password'], password):
            if user.get('is_banned'):
                return 'banned'
            return user
        return None

    @staticmethod
    def list_all():
        db = get_db()
        rows = db.execute(
            "SELECT id, username, email, phone_number, is_admin, is_banned, is_online, profile_photo, created_at FROM users ORDER BY created_at DESC"
        ).fetchall()
        return rows

    @staticmethod
    def update_profile_photo(user_id, image_path):
        db = get_db()
        db.execute("UPDATE users SET profile_photo = %s WHERE id = %s", (image_path, user_id))
        db.commit()

    @staticmethod
    def update_details(user_id, username, email, phone_number):
        db = get_db()
        db.execute(
            "UPDATE users SET username = %s, email = %s, phone_number = %s WHERE id = %s", 
            (username, email, phone_number, user_id)
        )
        db.commit()

    @staticmethod
    def update_password(user_id, new_password):
        db = get_db()
        hashed = generate_password_hash(new_password)
        db.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
        db.commit()

    @staticmethod
    def set_online(user_id, is_online):
        db = get_db()
        db.execute("UPDATE users SET is_online = %s WHERE id = %s", (1 if is_online else 0, user_id))
        db.commit()

    @staticmethod
    def update_role(user_id, is_admin):
        db = get_db()
        db.execute("UPDATE users SET is_admin = %s WHERE id = %s", (1 if is_admin else 0, user_id))
        db.commit()

    @staticmethod
    def ban(user_id):
        db = get_db()
        db.execute("UPDATE users SET is_banned = 1 WHERE id = %s", (user_id,))
        db.commit()

    @staticmethod
    def unban(user_id):
        db = get_db()
        db.execute("UPDATE users SET is_banned = 0 WHERE id = %s", (user_id,))
        db.commit()

    @staticmethod
    def delete(user_id):
        db = get_db()
        db.execute("DELETE FROM reports WHERE reporter_id = %s OR reported_user_id = %s", (user_id, user_id))
        db.execute("DELETE FROM wishlist WHERE user_id = %s", (user_id,))
        db.execute("DELETE FROM messages WHERE sender_id = %s OR recipient_id = %s", (user_id, user_id))
        db.execute("UPDATE items SET buyer_id = NULL WHERE buyer_id = %s", (user_id,))
        db.execute("DELETE FROM item_images WHERE item_id IN (SELECT id FROM items WHERE owner_id = %s)", (user_id,))
        db.execute("DELETE FROM items WHERE owner_id = %s", (user_id,))
        db.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()

    @staticmethod
    def get_stats():
        db = get_db()
        total = db.execute("SELECT COUNT(*) AS c FROM users").fetchone()['c']
        banned = db.execute("SELECT COUNT(*) AS c FROM users WHERE is_banned = 1").fetchone()['c']
        admins = db.execute("SELECT COUNT(*) AS c FROM users WHERE is_admin = 1").fetchone()['c']
        return {'total': total, 'banned': banned, 'admins': admins}
