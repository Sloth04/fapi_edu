import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# SECRETS
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USERNAME = os.getenv("DB_USERNAME", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_DATABASE = os.getenv("DB_DATABASE", "db_name")

# MAIL
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "username")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "********")
MAIL_FROM = os.getenv("MAIL_FROM", "test@example.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "mail server")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Test Admin Name").replace('_', ' ')

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
cwd = Path.cwd()
