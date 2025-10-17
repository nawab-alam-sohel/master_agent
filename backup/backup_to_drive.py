#!/usr/bin/env python3
"""
backup_to_drive.py

Usage: python backup/backup_to_drive.py

Environment variables required (set these in Render -> Environment):
- DATABASE_URL                 (postgres://... )  -- Render already has this
- GOOGLE_SERVICE_ACCOUNT_JSON  (the JSON content of your service account)
- GOOGLE_DRIVE_FOLDER_ID       (ID of the folder /render-backups/)
- BACKUP_PASSWORD              (your symmetric backup password, e.g. soheL8090@)

Notes:
- This script uses `pg_dump`. Ensure your Render instance has pg_dump available.
- If pg_dump is not available, the script will exit with instructions.
"""

import os
import sys
import subprocess
import shlex
import datetime
import tempfile
import json
import base64
from pathlib import Path

# Cryptography for encryption
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend

# Google Drive
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ---------- Config from env ----------
DATABASE_URL = os.getenv("DATABASE_URL")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
BACKUP_PASSWORD = os.getenv("BACKUP_PASSWORD")

if not DATABASE_URL:
    print("ERROR: DATABASE_URL is not set in env. Aborting.")
    sys.exit(1)
if not GOOGLE_SERVICE_ACCOUNT_JSON:
    print("ERROR: GOOGLE_SERVICE_ACCOUNT_JSON is not set in env. Aborting.")
    sys.exit(1)
if not GOOGLE_DRIVE_FOLDER_ID:
    print("ERROR: GOOGLE_DRIVE_FOLDER_ID is not set in env. Aborting.")
    sys.exit(1)
if not BACKUP_PASSWORD:
    print("ERROR: BACKUP_PASSWORD is not set in env. Aborting.")
    sys.exit(1)

# ---------- Helpers ----------
def ensure_pg_dump_available():
    try:
        out = subprocess.check_output(["pg_dump", "--version"], stderr=subprocess.STDOUT)
        print("Found pg_dump:", out.decode().strip())
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print("pg_dump check error:", str(e))
        return False

def run_pg_dump_to_file(database_url, out_path):
    # Use pg_dump with the full DATABASE_URL
    cmd = f'pg_dump "{database_url}" --format=custom --file="{out_path}"'
    print("Running:", cmd)
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise RuntimeError(f"pg_dump failed with exit code {proc.returncode}")

def derive_fernet_key_from_password(password: str, salt: bytes = None) -> (bytes, bytes):
    # if salt not supplied, generate 16 bytes
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

def encrypt_file_with_fernet(in_path: str, out_path: str, password: str):
    with open(in_path, "rb") as f:
        data = f.read()
    key, salt = derive_fernet_key_from_password(password)
    fernet = Fernet(key)
    token = fernet.encrypt(data)
    # Save salt + token to out file so we can recover later
    # Format: SALT(16 bytes) + token bytes
    with open(out_path, "wb") as f:
        f.write(salt + token)

def google_drive_upload(file_path: str, drive_folder_id: str, credentials_json_str: str):
    # write JSON to temp file for google credentials loader
    with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as jf:
        jf.write(credentials_json_str)
        jf.flush()
        jf_path = jf.name

    scopes = ['https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(jf_path, scopes=scopes)

    service = build('drive', 'v3', credentials=creds, cache_discovery=False)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [drive_folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/octet-stream', resumable=True)
    created = service.files().create(body=file_metadata, media_body=media, fields='id, name').execute()
    # cleanup
    try:
        os.remove(jf_path)
    except Exception:
        pass
    return created

# ---------- Main ----------
def main():
    print("Starting backup process:", datetime.datetime.utcnow().isoformat())
    if not ensure_pg_dump_available():
        print("\nERROR: pg_dump binary not found on this machine.")
        print("-> On Render, you must ensure the build environment includes the PostgreSQL client (pg_dump).")
        print("Typical solutions:")
        print("  - Use a custom Docker image that includes postgresql-client")
        print("  - Or run this backup from a separate runner that has pg_dump (e.g. your own server or GitHub Actions)")
        sys.exit(2)

    now = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    base_name = f"agent_152t-backup-{now}"
    tmp_dir = tempfile.mkdtemp(prefix="pg_backup_")
    dump_path = os.path.join(tmp_dir, base_name + ".dump")
    enc_path = os.path.join(tmp_dir, base_name + ".enc")

    try:
        # 1) Dump DB
        print("Dumping database to", dump_path)
        run_pg_dump_to_file(DATABASE_URL, dump_path)
        print("Dump completed.")

        # 2) Encrypt dump
        print("Encrypting dump to", enc_path)
        encrypt_file_with_fernet(dump_path, enc_path, BACKUP_PASSWORD)
        print("Encryption complete.")

        # 3) Upload to Google Drive
        print("Uploading to Google Drive folder ID:", GOOGLE_DRIVE_FOLDER_ID)
        res = google_drive_upload(enc_path, GOOGLE_DRIVE_FOLDER_ID, GOOGLE_SERVICE_ACCOUNT_JSON)
        print("Upload result:", res)

        print("Backup finished successfully.")
    except Exception as exc:
        print("Backup process failed:", str(exc))
        raise
    finally:
        # cleanup local files
        try:
            if os.path.exists(dump_path):
                os.remove(dump_path)
            if os.path.exists(enc_path):
                os.remove(enc_path)
            if os.path.isdir(tmp_dir):
                os.rmdir(tmp_dir)
        except Exception:
            pass

if __name__ == "__main__":
    main()
