import os
from dotenv import load_dotenv

# Load all variables from .env
load_dotenv()


class Config:
    """
    Main configuration class for the Flask backend
    """

    # ============================
    # Flask Secret Key (Sessions)
    # ============================
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")


    # ============================
    # Supabase Credentials
    # ============================
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


    # ============================
    # CORS Allowed Origins
    # ============================
    # ALLOWED_ORIGIN="*" will allow:
    # - Postman
    # - localhost
    # - 127.0.0.1
    # - LAN devices (192.x.x.x)
    ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")


    # ============================
    # Admin Login Credentials
    # ============================
    ADMIN_USERNAME = os.getenv("ADMIN_USER", "")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASS", "")
