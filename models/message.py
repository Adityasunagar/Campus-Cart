from utils.db import get_db


class Message:
    @staticmethod
    def send(sender_id, recipient_id, content):
        db = get_db()
        db.execute(
            "INSERT INTO messages (sender_id, recipient_id, content, is_read) VALUES (%s, %s, %s, %s)",
            (sender_id, recipient_id, content, 0),
        )
        db.commit()

    @staticmethod
    def list_conversation(user_id, recipient_id):
        db = get_db()
        rows = db.execute(
            "SELECT messages.*, sender.username AS sender_name, recipient.username AS recipient_name "
            "FROM messages "
            "JOIN users AS sender ON messages.sender_id = sender.id "
            "JOIN users AS recipient ON messages.recipient_id = recipient.id "
            "WHERE (messages.sender_id = %s AND messages.recipient_id = %s) "
            "OR (messages.sender_id = %s AND messages.recipient_id = %s) "
            "ORDER BY messages.created_at ASC",
            (user_id, recipient_id, recipient_id, user_id),
        ).fetchall()
        return rows

    @staticmethod
    def list_partners(user_id):
        db = get_db()
        rows = db.execute(
            "SELECT id, username, is_online, profile_photo FROM users WHERE id != %s AND is_admin = 0 ORDER BY username",
            (user_id,),
        ).fetchall()
        return rows

    @staticmethod
    def get_unread_count(user_id, sender_id):
        """Get count of unread messages from a specific sender"""
        db = get_db()
        row = db.execute(
            "SELECT COUNT(*) as count FROM messages WHERE recipient_id = %s AND sender_id = %s AND is_read = 0",
            (user_id, sender_id),
        ).fetchone()
        return row['count'] if row else 0

    @staticmethod
    def get_all_unread_counts(user_id):
        """Get unread message counts for each contact"""
        db = get_db()
        rows = db.execute(
            "SELECT sender_id, COUNT(*) as unread_count FROM messages "
            "WHERE recipient_id = %s AND is_read = 0 GROUP BY sender_id",
            (user_id,),
        ).fetchall()
        return {row['sender_id']: row['unread_count'] for row in rows} if rows else {}

    @staticmethod
    def mark_as_read(user_id, sender_id):
        """Mark all messages from a sender as read"""
        db = get_db()
        db.execute(
            "UPDATE messages SET is_read = 1 WHERE recipient_id = %s AND sender_id = %s AND is_read = 0",
            (user_id, sender_id),
        )
        db.commit()
