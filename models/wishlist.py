from utils.db import get_db


class Wishlist:
    @staticmethod
    def add(user_id, item_id):
        db = get_db()
        db.execute(
            "INSERT INTO wishlist (user_id, item_id) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (user_id, item_id),
        )
        db.commit()

    @staticmethod
    def remove(user_id, item_id):
        db = get_db()
        db.execute(
            "DELETE FROM wishlist WHERE user_id = %s AND item_id = %s",
            (user_id, item_id),
        )
        db.commit()

    @staticmethod
    def exists(user_id, item_id):
        db = get_db()
        row = db.execute(
            "SELECT 1 FROM wishlist WHERE user_id = %s AND item_id = %s",
            (user_id, item_id),
        ).fetchone()
        return bool(row)

    @staticmethod
    def list_for_user(user_id):
        db = get_db()
        rows = db.execute(
            "SELECT items.*, users.username AS owner_name FROM wishlist "
            "JOIN items ON wishlist.item_id = items.id "
            "JOIN users ON items.owner_id = users.id "
            "WHERE wishlist.user_id = %s "
            "ORDER BY wishlist.created_at DESC",
            (user_id,),
        ).fetchall()
        return rows
