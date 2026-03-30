import psycopg2
import psycopg2.extras
from flask import g
from werkzeug.security import generate_password_hash
from config import DATABASE_URL

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0,
    is_banned INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    price REAL NOT NULL,
    category VARCHAR(50) DEFAULT 'Other',
    owner_id INTEGER NOT NULL REFERENCES users(id),
    buyer_id INTEGER REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS item_images (
    id SERIAL PRIMARY KEY,
    item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    image_path VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES users(id),
    recipient_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wishlist (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    item_id INTEGER NOT NULL REFERENCES items(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, item_id)
);

CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    reporter_id INTEGER NOT NULL REFERENCES users(id),
    reported_user_id INTEGER REFERENCES users(id),
    reported_item_id INTEGER REFERENCES items(id),
    reason TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

class DBWrapper:
    def __init__(self, conn):
        self.conn = conn

    def execute(self, sql, params=None):
        sql = sql.replace('?', '%s')
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        if params is not None:
            cur.execute(sql, params)
        else:
            cur.execute(sql)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db():
    if 'db' not in g:
        conn = psycopg2.connect(DATABASE_URL)
        g.db = DBWrapper(conn)
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    # Attempt to create tables, ignoring db_dir logic as it's postgres now
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
                # Safe migrations for existing databases
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_banned INTEGER NOT NULL DEFAULT 0")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_online INTEGER DEFAULT 0")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo VARCHAR(255)")
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20)")
                cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'Other'")
                cur.execute("ALTER TABLE messages ADD COLUMN IF NOT EXISTS is_read INTEGER NOT NULL DEFAULT 0")
                # Seed admin user if no users exist
                cur.execute("SELECT COUNT(*) FROM users")
                row = cur.fetchone()
                if row is None or row[0] == 0:
                    cur.execute(
                        "INSERT INTO users (username, email, password, is_admin) VALUES (%s, %s, %s, %s)",
                        (
                            "admin",
                            "admin@campuscart.com",
                            generate_password_hash("admin123"),
                            1,
                        ),
                    )
            conn.commit()
    except Exception as e:
        print("Could not init DB:", e)

