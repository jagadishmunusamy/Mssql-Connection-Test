from datetime import timedelta
from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
)

app = Flask(__name__)

# --- config (dev) ---
app.config["JWT_SECRET_KEY"] = "dev-change-me"      # change in prod
app.config["JWT_TOKEN_LOCATION"] = ["cookies","headers"]  # allow both
app.config["JWT_COOKIE_SECURE"] = False             # True in prod (HTTPS)
app.config["JWT_COOKIE_SAMESITE"] = "Lax"           # <- capitalize L
app.config["JWT_COOKIE_CSRF_PROTECT"] = False       # keep False for Postman demo
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(seconds=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

jwt = JWTManager(app)

USER = {"username": "demo", "password": "demo", "role": "admin"}

# 1) LOGIN -> issue access + refresh
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    if data.get("username") != USER["username"] or data.get("password") != USER["password"]:
        return jsonify({"msg": "invalid credentials!"}), 401

    identity = USER["username"]                       # MUST be string
    claims   = {"role": USER["role"]}

    access  = create_access_token(identity=identity,  additional_claims=claims)
    refresh = create_refresh_token(identity=identity, additional_claims=claims)

    # Convenience: set BOTH cookies so you don't paste anything in Postman
    resp = jsonify({"msg": "logged in", "access_token": access})
    set_access_cookies(resp, access)     # access cookie (optional but handy)
    set_refresh_cookies(resp, refresh)   # refresh cookie (HTTP-only)
    return resp, 200

# 2) PROTECTED -> requires a valid ACCESS token (header or cookie)
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    username = get_jwt_identity()                    # "demo" (string)
    claims   = get_jwt()                             # dict (has "role")
    return jsonify({
        "hello": username,
        "role": claims.get("role")
    }), 200

# 3) REFRESH -> use the REFRESH cookie to mint a new access token
@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()                    # "demo"
    claims   = get_jwt()
    new_access = create_access_token(identity=identity, additional_claims={"role": claims.get("role")})

    # Set the new access token cookie so /protected works without copying
    resp = jsonify({"access_token": new_access})
    set_access_cookies(resp, new_access)

    # OPTIONAL (rotation): also issue a new refresh and set it again
    # new_refresh = create_refresh_token(identity=identity, additional_claims={"role": claims.get("role")})
    # set_refresh_cookies(resp, new_refresh)

    return resp, 200

# 4) LOGOUT -> clear both cookies
@app.route("/logout", methods=["POST"])
def logout():
    resp = jsonify({"msg": "logged out"})
    unset_jwt_cookies(resp)   # clears access + refresh cookies
    return resp, 200

if __name__ == "__main__":
    app.run(debug=True)
