import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# --- Load environment variables ---
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
BACKUP_PASSWORD = os.getenv("BACKUP_PASSWORD")

# --- Load Google credentials ---
creds = service_account.Credentials.from_service_account_file(
    "service_account.json",
    scopes=["https://www.googleapis.com/auth/drive"]
)

# --- Derive encryption key ---
def get_key(password, salt=b'1234567890123456'):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# --- Encrypt file ---
def encrypt_file(password):
    key = get_key(password)
    fernet = Fernet(key)
    with open("db.dump", "rb") as file:
        encrypted_data = fernet.encrypt(file.read())
    with open("db.enc", "wb") as file:
        file.write(encrypted_data)

# --- Upload to Google Drive ---
def upload_to_drive(file_path):
    service = build("drive", "v3", credentials=creds)
    file_metadata = {"name": os.path.basename(file_path), "parents": [GOOGLE_DRIVE_FOLDER_ID]}
    media = MediaFileUpload(file_path, mimetype="application/octet-stream")
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()

# --- Main backup logic ---
encrypt_file(BACKUP_PASSWORD)
upload_to_drive("db.enc")
print("✅ Backup uploaded to Google Drive successfully!")
