from utils.db import get_db


class Report:
    @staticmethod
    def create(reporter_id, reason, reported_user_id=None, reported_item_id=None):
        db = get_db()
        db.execute(
            "INSERT INTO reports (reporter_id, reported_user_id, reported_item_id, reason) VALUES (%s, %s, %s, %s)",
            (reporter_id, reported_user_id, reported_item_id, reason),
        )
        db.commit()

    @staticmethod
    def list_all():
        db = get_db()
        rows = db.execute(
            "SELECT reports.*, "
            "reporter.username AS reporter_name, "
            "reported_u.username AS reported_username, "
            "items.title AS reported_item_title "
            "FROM reports "
            "JOIN users AS reporter ON reports.reporter_id = reporter.id "
            "LEFT JOIN users AS reported_u ON reports.reported_user_id = reported_u.id "
            "LEFT JOIN items ON reports.reported_item_id = items.id "
            "WHERE reports.status = 'pending' "
            "ORDER BY reports.created_at DESC"
        ).fetchall()
        return rows

    @staticmethod
    def resolve(report_id):
        db = get_db()
        db.execute("UPDATE reports SET status = 'resolved' WHERE id = %s", (report_id,))
        db.commit()

    @staticmethod
    def count_pending():
        db = get_db()
        row = db.execute("SELECT COUNT(*) AS c FROM reports WHERE status = 'pending'").fetchone()
        return row['c'] if row else 0
