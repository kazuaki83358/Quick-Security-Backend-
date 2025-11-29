from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
from config import Config
from supabase_client import supabase
from functools import wraps

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Allow ALL origins (Postman, localhost, LAN, etc.)
CORS(app)


# ============================
# LOGIN REQUIRED DECORATOR
# ============================
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


# ============================
# HOME PAGE
# ============================
@app.route("/")
def home():
    return render_template("home.html")


# ============================
# PUBLIC API ENDPOINTS
# ============================

# ---------------------------------------
# CUSTOMER BOOKING (JSON ONLY)
# ---------------------------------------
@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.json

    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    booking = {
        "full_name": data.get("full_name"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "service_type": data.get("service_type"),
        "date": data.get("date"),
        "time": data.get("time"),
        "duration": data.get("duration"),
        "address": data.get("address"),
        "notes": data.get("notes"),
        "status": "requested"
    }

    result = supabase.table("bookings").insert(booking).execute()
    return jsonify({"message": "Booking submitted", "data": result.data}), 201


# ---------------------------------------
# WORKER APPLICATION (FORM + FILE UPLOAD)
# ---------------------------------------
@app.route("/api/workers", methods=["POST"])
def create_worker():
    data = request.form
    aadhaar_file = request.files.get("aadhaar")
    pan_file = request.files.get("pan")

    if not aadhaar_file or not pan_file:
        return jsonify({"error": "Aadhaar and PAN files required"}), 400

    bucket = "worker-documents"

    # Upload Aadhaar
    aadhaar_path = f"aadhaar/{aadhaar_file.filename}"
    supabase.storage.from_(bucket).upload(aadhaar_path, aadhaar_file.read())
    aadhaar_url = supabase.storage.from_(bucket).get_public_url(aadhaar_path)

    # Upload PAN
    pan_path = f"pan/{pan_file.filename}"
    supabase.storage.from_(bucket).upload(pan_path, pan_file.read())
    pan_url = supabase.storage.from_(bucket).get_public_url(pan_path)

    worker = {
        "full_name": data.get("full_name"),
        "phone": data.get("phone"),
        "email": data.get("email"),
        "city": data.get("city"),
        "service_type": data.get("service_type"),
        "experience": data.get("experience"),
        "availability": data.get("availability"),
        "address": data.get("address"),
        "certifications": data.get("certifications"),
        "info": data.get("info"),
        "aadhaar_url": aadhaar_url,
        "pan_url": pan_url,
        "status": "pending"
    }

    supabase.table("workers").insert(worker).execute()
    return jsonify({"message": "Application submitted"}), 201


# ============================
# ADMIN PANEL
# ============================

@app.route("/admin")
@login_required
def admin_home():
    return redirect(url_for("admin_bookings"))


# ---- LOGIN ----
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if (
            request.form["username"] == Config.ADMIN_USERNAME
            and request.form["password"] == Config.ADMIN_PASSWORD
        ):
            session["admin_logged_in"] = True
            return redirect(url_for("admin_bookings"))

        return render_template("login.html", error="Invalid login")

    return render_template("login.html")


# ---- LOGOUT ----
@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


# ---- BOOKINGS TABLE ----
@app.route("/admin/bookings")
@login_required
def admin_bookings():
    result = (
        supabase
        .table("bookings")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return render_template("admin_bookings.html", bookings=result.data)


# ---- WORKERS TABLE ----
@app.route("/admin/workers")
@login_required
def admin_workers():
    result = (
        supabase
        .table("workers")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return render_template("admin_workers.html", workers=result.data)


# ---- UPDATE BOOKING STATUS ----
@app.route("/admin/update/booking/<id>/<status>")
@login_required
def update_booking_status(id, status):
    supabase.table("bookings").update({"status": status}).eq("id", id).execute()
    return redirect(url_for("admin_bookings"))


# ---- UPDATE WORKER STATUS ----
@app.route("/admin/update/worker/<id>/<status>")
@login_required
def update_worker_status(id, status):
    supabase.table("workers").update({"status": status}).eq("id", id).execute()
    return redirect(url_for("admin_workers"))


# ============================
# RUN SERVER
# ============================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
