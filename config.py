import bcrypt
from pathlib import Path

# --- paths ----------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "autoservice.db"

# --- server ---------------------------------------------------------------

HOST = "0.0.0.0"
PORT = 8000

# --- sessions -------------------------------------------------------------

SESSION_SECRET  = "change-this-to-a-random-string-before-deploy"
SESSION_MAX_AGE = 60 * 60 * 2 # 2 hours in seconds

# --- admin login ----------------------------------------------------------
# admin login is still in code — only password is in DB
ADMIN_LOGIN = "admin"

# --- password hashing -----------------------------------------------------

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# --- read passwords from DB -----------------------------------------------
# imported lazily to avoid circular imports at module load time

def get_user_password_hash() -> str:
    from database import get_setting
    return get_setting("user_password_hash") or ""


def get_admin_password_hash() -> str:
    from database import get_setting
    return get_setting("admin_password_hash") or ""