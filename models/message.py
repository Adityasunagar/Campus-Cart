from utils.db import get_db


class Message:
    @staticmethod
    def send(sender_id, recipient_id, content):
        db = get_db()
        db.execute(
            "INSERT INTO messages (sender_id, recipient_id, content) VALUES (%s, %s, %s)",
            (sender_id, recipient_id, content),
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
            "SELECT id, username FROM users WHERE id != %s ORDER BY username",
            (user_id,),
        ).fetchall()
        return rows
