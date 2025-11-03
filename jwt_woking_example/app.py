from datetime import timedelta
from pathlib import Path
from flask import Flask, jsonify, request, make_response, send_from_directory
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    set_refresh_cookies,
    unset_jwt_cookies,
)

app = Flask(__name__, static_folder="static", static_url_path="")
app.config["JWT_SECRET_KEY"] = "dev-change-me"
app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
app.config["JWT_COOKIE_SECURE"] = False         # True in prod (HTTPS)
app.config["JWT_COOKIE_SAMESITE"] = "Lax"
app.config["JWT_COOKIE_CSRF_PROTECT"] = False   # Enable & handle in prod
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=15)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

jwt = JWTManager(app)

@app.post("/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"ok": False, "message": "username & password required"}), 400

    # TODO: validate credentials
    identity = username  # dict identity (avoid “string indices” bug)
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    resp = make_response(jsonify({"ok": True, "access_token": access_token}))
    set_refresh_cookies(resp, refresh_token)  # HttpOnly cookie
    return resp

@app.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    user = get_jwt_identity()
    new_access = create_access_token(identity=user)
    return jsonify({"ok": True, "access_token": new_access})

@app.post("/auth/logout")
def logout():
    resp = make_response(jsonify({"ok": True}))
    unset_jwt_cookies(resp)
    return resp

@app.get("/api/hello")
@jwt_required()
def hello():
    user = get_jwt_identity()
    return jsonify({"ok": True, "message": f"Hello {user} 👋"})

# Serve the two pages
@app.get("/")
def root():
    return send_from_directory(app.static_folder, "login.html")

@app.get("/dashboard")
def dashboard():
    return send_from_directory(app.static_folder, "dashboard.html")

# add to app.py
@app.get("/reports")
def reports():
    return send_from_directory(app.static_folder, "reports.html")

if __name__ == "__main__":
    Path("static").mkdir(exist_ok=True)
    app.run(host="0.0.0.0", port=5050, debug=True)
