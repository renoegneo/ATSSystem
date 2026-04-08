import bcrypt
from pathlib import Path

# --- paths ----------------------------------------------------------------

BASE_DIR = Path(__file__).parent
DB_PATH  = BASE_DIR / "autoservice.db"

# --- server ---------------------------------------------------------------

HOST = "0.0.0.0"  # listen on all network interfaces, not just localhost
PORT = 8000

# --- sessions -------------------------------------------------------------

SESSION_SECRET = "change-this-to-a-random-string-before-deploy"
SESSION_MAX_AGE = 60 * 60   # 1 hour in seconds


# --- password hashing -----------------------------------------------------

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# --- credentials ----------------------------------------------------------
# To change passwords: replace the hash with hash_password("your_new_password")
# Run this once in terminal to generate a hash:
#   python -c "from config import hash_password; print(hash_password('yourpassword'))"

USER_PASSWORD_HASH  = hash_password("1234")  # change before deploy
ADMIN_LOGIN         = "admin"
ADMIN_PASSWORD_HASH = hash_password("admin") # change before deploy