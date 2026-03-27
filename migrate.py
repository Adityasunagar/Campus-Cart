import psycopg2
from config import DATABASE_URL

def migrate():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS buyer_id INTEGER REFERENCES users(id)")
                except Exception as e:
                    print("Could not add buyer_id:", e)
                    conn.rollback()

                try:
                    cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'available'")
                except Exception as e:
                    print("Could not add status:", e)
                    conn.rollback()

                cur.execute("""
                    CREATE TABLE IF NOT EXISTS item_images (
                        id SERIAL PRIMARY KEY,
                        item_id INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
                        image_path VARCHAR(255) NOT NULL
                    )
                """)

                try:
                    cur.execute("ALTER TABLE items ADD COLUMN IF NOT EXISTS category VARCHAR(50) DEFAULT 'Other'")
                except Exception as e:
                    print("Could not add category:", e)
                    conn.rollback()
            conn.commit()
            print("Migration successful")
    except Exception as e:
        print("Migration failed overall:", e)

if __name__ == '__main__':
    migrate()
