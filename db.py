import os
import psycopg2
import psycopg2.pool
from psycopg2.extras import RealDictCursor
from flask import g

DATABASE_URL = os.environ.get('DATABASE_URL', '')

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    price REAL NOT NULL,
    image_url TEXT NOT NULL DEFAULT '',
    video_url TEXT DEFAULT '',
    sizes TEXT DEFAULT '',
    colors TEXT DEFAULT '',
    category TEXT NOT NULL DEFAULT 'general',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    customer_phone TEXT NOT NULL,
    customer_address TEXT NOT NULL,
    wilaya TEXT DEFAULT '',
    wilaya_id INTEGER DEFAULT 0,
    commune TEXT DEFAULT '',
    delivery_type TEXT DEFAULT 'domicile',
    delivery_price REAL DEFAULT 0,
    notes TEXT DEFAULT '',
    total_amount REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    item_size TEXT DEFAULT '',
    item_color TEXT DEFAULT '',
    FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_created ON products(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_phone ON orders(customer_phone);
CREATE INDEX IF NOT EXISTS idx_orders_created ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
"""

_pool = None

def get_pool():
    global _pool
    if _pool is None and DATABASE_URL:
        _pool = psycopg2.pool.ThreadedConnectionPool(1, 10, DATABASE_URL)
    return _pool

def get_db():
    if 'db' not in g:
        pool = get_pool()
        if pool:
            g.db = pool.getconn()
        else:
            g.db = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        pool = get_pool()
        if pool:
            pool.putconn(db)
        else:
            db.close()

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(SCHEMA)
    conn.commit()
    cur.close()
    conn.close()

def query(sql, params=()):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return rows

def query_one(sql, params=()):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    row = cur.fetchone()
    cur.close()
    return row

def execute(sql, params=()):
    db = get_db()
    cur = db.cursor(cursor_factory=RealDictCursor)
    cur.execute(sql, params)
    db.commit()
    lastrowid = None
    if cur.description:
        row = cur.fetchone()
        if row:
            lastrowid = row.get('id')
    cur.close()
    return lastrowid
