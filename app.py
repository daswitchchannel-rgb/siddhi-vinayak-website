from flask import Flask, request, jsonify, send_from_directory, session, redirect
from pathlib import Path
import sqlite3, os, secrets
from werkzeug.utils import secure_filename
from flask import send_file
import mimetypes
import os

BASE=Path(__file__).resolve().parent
DB=BASE/"data.db"
UPLOAD=BASE/"uploads"; UPLOAD.mkdir(exist_ok=True)
app=Flask(__name__, static_folder="static")
MAX_UPLOAD_MB=int(os.environ.get("MAX_UPLOAD_MB", "50"))
app.config["MAX_CONTENT_LENGTH"]=MAX_UPLOAD_MB*1024*1024
app.secret_key=os.environ.get("SECRET_KEY", secrets.token_hex(32))
ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", "change-me")
ALLOWED_EXT={".jpg",".jpeg",".png",".webp",".gif",".mp4",".webm",".mov"}
def db():
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        c = psycopg2.connect(
    database_url,
    sslmode="require",
    cursor_factory=RealDictCursor
)
return c
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c
def init():
    c=db()
      c.execute("""
        CREATE TABLE IF NOT EXISTS materials(
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS designs(
            id SERIAL PRIMARY KEY,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            material TEXT,
            application TEXT,
            description TEXT,
            image TEXT,
            video TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS products(
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            code TEXT,
            price TEXT,
            description TEXT,
            image TEXT,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS inquiries(
            id SERIAL PRIMARY KEY,
            name TEXT,
            phone TEXT,
            type TEXT,
            material TEXT,
            reference TEXT,
            message TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    if c.execute("SELECT COUNT(*) n FROM materials").fetchone()["n"]==0:
        for n,cat in [("Sandstone","Stone"),("Gwalior Mint","Stone"),("Jaisalmer Yellow","Stone"),("Bansi Paharpur","Stone"),("Granite","Stone"),("Marble","Stone"),("HDHMR","Wood & Boards"),("MDF","Wood & Boards"),("WPC","Wood & Boards"),("PVC","Wood & Boards"),("Corian / Solid Surface","Solid Surface"),("ACP","Exterior"),("Aluminium","Metal"),("Brass","Metal"),("Copper","Metal")]:
            c.execute("INSERT INTO materials(name,category) VALUES(?,?)",(n,cat))
    c.commit(); c.close()
init()

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")
@app.get("/admin")
def admin():
    return send_from_directory(app.static_folder, "admin.html")
@app.get("/uploads/<path:name>")
def uploads(name):
    # Only serve files that exist inside the controlled upload directory.
    p=(UPLOAD/name).resolve()
    if UPLOAD.resolve() not in p.parents: return jsonify(error="invalid path"),400
    return send_from_directory(UPLOAD,p.name)

@app.post("/api/login")
def login():
    if request.json.get("password")==ADMIN_PASSWORD:
        session["admin"]=True; return jsonify(ok=True)
    return jsonify(ok=False,error="Invalid password"),401
@app.post("/api/logout")
def logout(): session.clear(); return jsonify(ok=True)

def auth():
    return session.get("admin",False)

@app.get("/api/catalog")
def catalog():
    c=db()
    out={
        "materials":[dict(x) for x in c.execute(
            "SELECT * FROM materials ORDER BY id DESC"
        ).fetchall()],
        "designs":[dict(x) for x in c.execute(
            "SELECT * FROM designs ORDER BY id DESC"
        ).fetchall()],
        "products":[dict(x) for x in c.execute(
            "SELECT * FROM products WHERE active=1 ORDER BY id DESC"
        ).fetchall()]
    }
    c.close()
    return jsonify(out)


@app.get("/api/admin/data")
def admin_data():
    if not auth():
        return jsonify(error="login required"),401

    c=db()
    out={
        "materials":[dict(x) for x in c.execute(
            "SELECT * FROM materials ORDER BY id DESC"
        ).fetchall()],
        "designs":[dict(x) for x in c.execute(
            "SELECT * FROM designs ORDER BY id DESC"
        ).fetchall()],
        "products":[dict(x) for x in c.execute(
            "SELECT * FROM products ORDER BY id DESC"
        ).fetchall()],
        "inquiries":[dict(x) for x in c.execute(
            "SELECT * FROM inquiries ORDER BY id DESC"
        ).fetchall()]
    }
    c.close()
    return jsonify(out)

@app.post("/api/materials")
def add_material():
    if not auth(): return jsonify(error="login required"),401
    x=request.json;c=db();c.execute("INSERT INTO materials(name,category,description) VALUES(?,?,?)",(x["name"],x["category"],x.get("description","")));c.commit();c.close();return jsonify(ok=True)

@app.post("/api/designs")
def add_design():
    if not auth(): return jsonify(error="login required"),401
    x=request.json;c=db()
    try:c.execute("INSERT INTO designs(code,title,material,application,description,image,video) VALUES(?,?,?,?,?,?,?)",(x["code"],x["title"],x.get("material",""),x.get("application",""),x.get("description",""),x.get("image",""),x.get("video","")));c.commit()
    except sqlite3.IntegrityError:return jsonify(error="Design code already exists"),409
    finally:c.close()
    return jsonify(ok=True)

@app.post("/api/products")
def add_product():
    if not auth(): return jsonify(error="login required"),401
    x=request.json;c=db();c.execute("INSERT INTO products(name,code,price,description,image) VALUES(?,?,?,?,?)",(x["name"],x.get("code",""),x.get("price","Custom quote"),x.get("description",""),x.get("image","")));c.commit();c.close();return jsonify(ok=True)

@app.post("/api/inquiries")
def inquiry():
    x=request.json;c=db();c.execute("INSERT INTO inquiries(name,phone,type,material,reference,message) VALUES(?,?,?,?,?,?)",(x.get("name"),x.get("phone"),x.get("type"),x.get("material"),x.get("reference"),x.get("message")));c.commit();c.close();return jsonify(ok=True)

@app.post("/api/upload")
def upload():
    if not auth(): return jsonify(error="login required"),401
    f=request.files.get("file")
    if not f: return jsonify(error="No file"),400
    original=secure_filename(f.filename or "")
    ext=Path(original).suffix.lower()
    if not original or ext not in ALLOWED_EXT:
        return jsonify(error="Unsupported file type"),400
    stem=secrets.token_hex(8)+"_"+original
    f.save(UPLOAD/stem)
    return jsonify(url="/uploads/"+stem)

@app.delete("/api/<table>/<int:item_id>")
def delete(table,item_id):
    if not auth() or table not in {"materials","designs","products"}: return jsonify(error="not allowed"),403
    c=db();c.execute(f"DELETE FROM {table} WHERE id=?",(item_id,));c.commit();c.close();return jsonify(ok=True)


@app.get("/api/health")
def health():
    return jsonify(ok=True,service="siddhi-vinayak",version="7")

@app.after_request
def security_headers(resp):
    resp.headers["X-Content-Type-Options"]="nosniff"
    resp.headers["X-Frame-Options"]="SAMEORIGIN"
    resp.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
    return resp

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=True)
