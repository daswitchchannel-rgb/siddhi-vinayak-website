from flask import Flask, request, jsonify, send_from_directory, session
from pathlib import Path
import sqlite3
import os
import secrets
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor

BASE = Path(__file__).resolve().parent
DB = BASE / "data.db"
UPLOAD = BASE / "uploads"
UPLOAD.mkdir(exist_ok=True)

app = Flask(__name__, static_folder="static")
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "25"))
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-me")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm", ".mov"}

class PostgresDB:
    def __init__(self, url):
        self.conn = psycopg2.connect(url, sslmode="require", cursor_factory=RealDictCursor)
    def execute(self, query, params=None):
        cur = self.conn.cursor()
        cur.execute(query, params)
        return cur
    def commit(self): self.conn.commit()
    def rollback(self): self.conn.rollback()
    def close(self): self.conn.close()

def using_postgres():
    return bool(os.environ.get("DATABASE_URL"))

def db():
    if using_postgres():
        return PostgresDB(os.environ["DATABASE_URL"])
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def qmarks(sql):
    return sql.replace("?", "%s") if using_postgres() else sql

def init():
    c = db()
    if using_postgres():
        c.execute("""CREATE TABLE IF NOT EXISTS materials(
            id SERIAL PRIMARY KEY, name TEXT NOT NULL, category TEXT NOT NULL,
            description TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS designs(
            id SERIAL PRIMARY KEY, code TEXT UNIQUE NOT NULL, title TEXT NOT NULL,
            material TEXT, application TEXT, description TEXT, image TEXT, video TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS products(
            id SERIAL PRIMARY KEY, name TEXT NOT NULL, code TEXT, price TEXT,
            description TEXT, image TEXT, active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS inquiries(
            id SERIAL PRIMARY KEY, name TEXT, phone TEXT, type TEXT, material TEXT,
            reference TEXT, message TEXT, status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    else:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS materials(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,category TEXT NOT NULL,description TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS designs(id INTEGER PRIMARY KEY AUTOINCREMENT,code TEXT UNIQUE NOT NULL,title TEXT NOT NULL,material TEXT,application TEXT,description TEXT,image TEXT,video TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,code TEXT,price TEXT,description TEXT,image TEXT,active INTEGER DEFAULT 1,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS inquiries(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,phone TEXT,type TEXT,material TEXT,reference TEXT,message TEXT,status TEXT DEFAULT 'new',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
    row = c.execute("SELECT COUNT(*) AS n FROM materials").fetchone()
    if row["n"] == 0:
        items = [
            ("Sandstone","Stone"),("Gwalior Mint","Stone"),("Jaisalmer Yellow","Stone"),
            ("Bansi Paharpur","Stone"),("Pink Stone","Stone"),("Granite","Stone"),
            ("Marble","Stone"),("HDHMR","Wood & Boards"),("HDF","Wood & Boards"),
            ("MDF","Wood & Boards"),("Plywood","Wood & Boards"),("WPC","Wood & Boards"),
            ("PVC","Wood & Boards"),("Corian / Solid Surface","Solid Surface"),
            ("ACP","Exterior"),("Aluminium","Metal"),("Brass","Metal"),("Copper","Metal")]
        sql = qmarks("INSERT INTO materials(name,category) VALUES(?,?)")
        for name, category in items:
            c.execute(sql, (name, category))
    c.commit()
    c.close()

init()

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.get("/admin")
def admin():
    return send_from_directory(app.static_folder, "admin.html")

@app.get("/uploads/<path:name>")
def uploads(name):
    p = (UPLOAD / name).resolve()
    if UPLOAD.resolve() not in p.parents:
        return jsonify(error="invalid path"), 400
    return send_from_directory(UPLOAD, p.name)

@app.post("/api/login")
def login():
    payload = request.get_json(silent=True) or {}
    if payload.get("password") == ADMIN_PASSWORD:
        session["admin"] = True
        return jsonify(ok=True)
    return jsonify(ok=False, error="Invalid password"), 401

@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)

def auth():
    return bool(session.get("admin"))

def rows(c, sql):
    return [dict(x) for x in c.execute(sql).fetchall()]

@app.get("/api/catalog")
def catalog():
    c = db()
    out = {
        "materials": rows(c, "SELECT * FROM materials ORDER BY id DESC"),
        "designs": rows(c, "SELECT * FROM designs ORDER BY id DESC"),
        "products": rows(c, "SELECT * FROM products WHERE active=1 ORDER BY id DESC")}
    c.close()
    return jsonify(out)

@app.get("/api/admin/data")
def admin_data():
    if not auth():
        return jsonify(error="login required"), 401
    c = db()
    out = {
        "materials": rows(c, "SELECT * FROM materials ORDER BY id DESC"),
        "designs": rows(c, "SELECT * FROM designs ORDER BY id DESC"),
        "products": rows(c, "SELECT * FROM products ORDER BY id DESC"),
        "inquiries": rows(c, "SELECT * FROM inquiries ORDER BY id DESC")}
    c.close()
    return jsonify(out)

@app.post("/api/materials")
def add_material():
    if not auth(): return jsonify(error="login required"), 401
    x = request.get_json(silent=True) or {}
    if not x.get("name") or not x.get("category"):
        return jsonify(error="name and category are required"), 400
    c = db()
    c.execute(qmarks("INSERT INTO materials(name,category,description) VALUES(?,?,?)"),
              (x["name"], x["category"], x.get("description", "")))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.post("/api/designs")
def add_design():
    if not auth(): return jsonify(error="login required"), 401
    x = request.get_json(silent=True) or {}
    if not x.get("code") or not x.get("title"):
        return jsonify(error="code and title are required"), 400
    c = db()
    try:
        c.execute(qmarks("INSERT INTO designs(code,title,material,application,description,image,video) VALUES(?,?,?,?,?,?,?)"),
                  (x["code"], x["title"], x.get("material",""), x.get("application",""),
                   x.get("description",""), x.get("image",""), x.get("video","")))
        c.commit()
    except (sqlite3.IntegrityError, psycopg2.IntegrityError):
        c.rollback()
        return jsonify(error="Design code already exists"), 409
    finally:
        c.close()
    return jsonify(ok=True)

@app.post("/api/products")
def add_product():
    if not auth(): return jsonify(error="login required"), 401
    x = request.get_json(silent=True) or {}
    if not x.get("name"): return jsonify(error="name is required"), 400
    c = db()
    c.execute(qmarks("INSERT INTO products(name,code,price,description,image) VALUES(?,?,?,?,?)"),
              (x["name"], x.get("code",""), x.get("price","Custom quote"),
               x.get("description",""), x.get("image","")))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.post("/api/inquiries")
def inquiry():
    x = request.get_json(silent=True) or {}
    c = db()
    c.execute(qmarks("INSERT INTO inquiries(name,phone,type,material,reference,message) VALUES(?,?,?,?,?,?)"),
              (x.get("name"), x.get("phone"), x.get("type"), x.get("material"),
               x.get("reference"), x.get("message")))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.post("/api/upload")
def upload():
    if not auth(): return jsonify(error="login required"), 401
    f = request.files.get("file")
    if not f: return jsonify(error="No file"), 400
    original = secure_filename(f.filename or "")
    ext = Path(original).suffix.lower()
    if not original or ext not in ALLOWED_EXT:
        return jsonify(error="Unsupported file type"), 400
    stem = secrets.token_hex(8) + "_" + original
    f.save(UPLOAD / stem)
    return jsonify(url="/uploads/" + stem)

@app.delete("/api/<table>/<int:item_id>")
def delete(table, item_id):
    if not auth() or table not in {"materials","designs","products"}:
        return jsonify(error="not allowed"), 403
    c = db()
    c.execute(qmarks("DELETE FROM %s WHERE id=?" % table), (item_id,))
    c.commit(); c.close()
    return jsonify(ok=True)

@app.get("/api/health")
def health():
    c = db()
    c.execute("SELECT 1").fetchone()
    c.close()
    return jsonify(ok=True, service="siddhi-vinayak", version="10",
                   database="postgres" if using_postgres() else "sqlite")

@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["X-Frame-Options"] = "SAMEORIGIN"
    resp.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=True)
