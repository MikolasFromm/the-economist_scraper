#!/usr/bin/env python3
"""The Economist EPUB downloader

Downloads the latest issue from https://github.com/evanbio/The_Economist
which publishes weekly issues every Sunday in TE-YYYY-MM-DD directories.

Functions:
- get_latest_issue() -> (date_str, dir_name)
- download_latest(save_path) -> file_path
- send_latest_issue(recipients, attachment_path, kindle)

Env vars for sending:
  SENDER_EMAIL, SENDER_EMAIL_PASSWORD
  SMTP_SERVER (default: smtp.gmail.com), SMTP_PORT (default: 465)
"""
from __future__ import annotations
import os
import re
import ssl
import smtplib
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import requests

GITHUB_API = "https://api.github.com/repos/evanbio/The_Economist/contents/"
RAW_BASE = "https://raw.githubusercontent.com/evanbio/The_Economist/main"
DIR_RE = re.compile(r"^TE-(\d{4}-\d{2}-\d{2})$")
EPUB_DIR = "epubs"

EMAIL_SENDER = os.environ.get("SENDER_EMAIL")
EMAIL_SENDER_PASSWORD = os.environ.get("SENDER_EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))


def get_latest_issue() -> tuple[str, str]:
    """Return (date_str, dir_name) for the most recently published issue."""
    r = requests.get(GITHUB_API, headers={"Accept": "application/vnd.github+json", "User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    entries = r.json()
    dirs = []
    for entry in entries:
        if entry.get("type") == "dir":
            m = DIR_RE.match(entry["name"])
            if m:
                dirs.append((m.group(1), entry["name"]))
    if not dirs:
        raise SystemExit("No TE-YYYY-MM-DD directories found in repository.")
    dirs.sort(key=lambda x: x[0], reverse=True)
    return dirs[0]


def download_latest(save_path: str = EPUB_DIR) -> Optional[str]:
    """Download the latest issue EPUB and return its path."""
    date_str, dir_name = get_latest_issue()
    year = date_str[:4]
    year_dir = os.path.join(save_path, year)
    os.makedirs(year_dir, exist_ok=True)

    fname = f"{dir_name}.epub"
    out_path = os.path.join(year_dir, fname)

    url = f"{RAW_BASE}/{dir_name}/{fname}"
    print(f"Downloading {url}")
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True)
    if r.status_code != 200:
        print(f"Download failed: {r.status_code}")
        return None

    with open(out_path, "wb") as f:
        for chunk in r.iter_content(8192):
            if chunk:
                f.write(chunk)
    print(f"Saved {out_path}")
    return out_path


def send_latest_issue(recipients: str, attachment_path: Optional[str] = None, kindle: bool = False):
    """Send EPUB to recipients (semicolon-separated).

    For Kindle recipients, pass kindle=True and a single address.
    """
    if not EMAIL_SENDER or not EMAIL_SENDER_PASSWORD:
        print("Sender credentials not set (SENDER_EMAIL / SENDER_EMAIL_PASSWORD). Skipping email.")
        return

    to_list = [r.strip() for r in recipients.split(";") if r.strip()]
    if not to_list:
        print("No recipients. Skipping email.")
        return

    if kindle and len(to_list) > 1:
        raise ValueError("Kindle delivery requires exactly one recipient per call.")

    message = MIMEMultipart("alternative")
    message["From"] = EMAIL_SENDER
    if kindle:
        message["To"] = to_list[0]
        body = ""
    else:
        message["Subject"] = "The Economist - Latest Issue"
        message["To"] = EMAIL_SENDER
        body = "<h1>The Economist – Latest Issue</h1><p>This week's issue is attached. Enjoy reading!</p>"

    message.attach(MIMEText(body, "html"))

    if not attachment_path or not os.path.exists(attachment_path):
        print("Attachment not found. Aborting email.")
        return

    ctype, _ = mimetypes.guess_type(attachment_path)
    if ctype is None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    with open(attachment_path, "rb") as fp:
        part = MIMEBase(maintype, subtype)
        part.set_payload(fp.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(attachment_path)}"')
    message.attach(part)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_SENDER_PASSWORD)
            server.sendmail(EMAIL_SENDER, to_list, message.as_string())
        print(f"Email sent: {attachment_path} → {', '.join(to_list)}")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--latest", action="store_true", help="download latest issue and optionally send")
    p.add_argument("--save-path", default=EPUB_DIR, help="directory to save EPUBs")
    p.add_argument("--recipients", help="semicolon-separated email recipients")
    p.add_argument("--kindle-recipients", help="semicolon-separated Kindle email addresses")
    args = p.parse_args()

    if not args.latest:
        raise SystemExit("Please provide --latest.")

    path = download_latest(save_path=args.save_path)
    if path:
        if args.recipients:
            send_latest_issue(recipients=args.recipients, attachment_path=path, kindle=False)
        if args.kindle_recipients:
            for recipient in args.kindle_recipients.split(";"):
                recipient = recipient.strip()
                if recipient:
                    send_latest_issue(recipients=recipient, attachment_path=path, kindle=True)


if __name__ == "__main__":
    main()
