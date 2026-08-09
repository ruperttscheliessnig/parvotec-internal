#!/usr/bin/env python3
"""
Upload Parvotec ASGCT 2026 videos to YouTube as UNLISTED.
Requires: pip install google-api-python-client google-auth-oauthlib

Setup (einmalig):
  1. Google Cloud Console → APIs & Services → Enable YouTube Data API v3
  2. Credentials → Create OAuth 2.0 Client ID (Desktop app)
  3. Download JSON → save as client_secrets.json next to this script
  4. Run: python3 upload_to_youtube.py
  5. Browser öffnet für OAuth-Login (einmalig)
  6. Token wird lokal gespeichert → danach automatisch
"""

import os
import sys
import json
import time
import pickle
from pathlib import Path

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-api-python-client google-auth-oauthlib")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
SECRETS_FILE = Path(__file__).parent / "client_secrets.json"
TOKEN_FILE   = Path(__file__).parent / "youtube_token.pickle"
OUTPUT_FILE  = Path(__file__).parent / "youtube_ids.json"  # IDs written here
VIDEO_DIR    = Path.home() / "workspace-active/parvotec/Machine learning for Rupert/ASGCT2026"

# ─── Videos mit Titeln ───────────────────────────────────────────────────────
VIDEOS = [
    {
        "file": VIDEO_DIR / "AAV_Engineering_III.mp4",
        "key":  "AAV_Engineering_III",
        "title": "AAV Engineering III — Capsid Engineering Session · ASGCT 2026",
        "description": "ASGCT 2026 conference recording. Capsid engineering session. calyr.aí Research / Parvotec Project.",
    },
    {
        "file": VIDEO_DIR / "AAV_Engineering_IV.mp4",
        "key":  "AAV_Engineering_IV",
        "title": "AAV Engineering IV — Capsid Engineering Session · ASGCT 2026",
        "description": "ASGCT 2026 conference recording. Capsid engineering session (part IV). calyr.aí Research / Parvotec Project.",
    },
    {
        "file": VIDEO_DIR / "AAV_Trafficking.mp4",
        "key":  "AAV_Trafficking",
        "title": "AAV Trafficking — Intracellular Transport Session · ASGCT 2026",
        "description": "ASGCT 2026 conference recording. AAV intracellular trafficking. calyr.aí Research / Parvotec Project.",
    },
    {
        "file": VIDEO_DIR / "Lir_AAV_LLM.mp4",
        "key":  "Lir_AAV_LLM",
        "title": "Lir / Peacock — Corsair Protein Language Model · ASGCT 2026",
        "description": "ASGCT 2026 conference recording. Protein language model for AAV design. calyr.aí Research / Parvotec Project.",
    },
    {
        "file": VIDEO_DIR / "ShapeTX_AAV5engineering.mp4",
        "key":  "ShapeTX_AAV5engineering",
        "title": "ShapeTX — AAV5 Engineering · ASGCT 2026",
        "description": "ASGCT 2026 conference recording. AAV5 capsid engineering by ShapeTX. calyr.aí Research / Parvotec Project.",
    },
    {
        "file": VIDEO_DIR / "TuningReceptorInteractions_Caltech.mp4",
        "key":  "TuningReceptorInteractions_Caltech",
        "title": "Tuning Receptor Interactions — Caltech · ASGCT 2026",
        "description": "ASGCT 2026 conference recording. Receptor interaction tuning for AAV. calyr.aí Research / Parvotec Project.",
    },
]


def get_credentials():
    """OAuth2 — opens browser on first run, uses saved token thereafter."""
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not SECRETS_FILE.exists():
                print(f"ERROR: {SECRETS_FILE} not found.")
                print("Download OAuth 2.0 credentials from Google Cloud Console.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(str(SECRETS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "wb") as f:
            pickle.dump(creds, f)
    return creds


def upload_video(youtube, video):
    """Upload a single video and return its YouTube ID."""
    filepath = video["file"]
    if not filepath.exists():
        print(f"  SKIP (not found): {filepath}")
        return None

    size_gb = filepath.stat().st_size / 1e9
    print(f"\n→ Uploading: {video['key']} ({size_gb:.1f} GB)")

    body = {
        "snippet": {
            "title":       video["title"],
            "description": video["description"],
            "tags":        ["AAV", "ASGCT", "gene therapy", "parvotec", "calyr"],
            "categoryId":  "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": "unlisted",  # NOT public, NOT searchable
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        str(filepath),
        mimetype="video/mp4",
        resumable=True,
        chunksize=50 * 1024 * 1024,  # 50MB chunks
    )

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    last_progress = 0
    while response is None:
        status, response = request.next_chunk()
        if status:
            progress = int(status.progress() * 100)
            if progress >= last_progress + 10:
                print(f"  {progress}% uploaded...")
                last_progress = progress

    video_id = response["id"]
    print(f"  ✓ Done: https://youtu.be/{video_id}")
    return video_id


def main():
    print("=== Parvotec YouTube Upload ===\n")

    creds   = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    # Load existing IDs (resume if interrupted)
    ids = {}
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE) as f:
            ids = json.load(f)
        print(f"Resuming — {len(ids)} videos already uploaded.\n")

    for video in VIDEOS:
        key = video["key"]
        if key in ids:
            print(f"  ~ {key} already uploaded: {ids[key]}")
            continue

        try:
            video_id = upload_video(youtube, video)
            if video_id:
                ids[key] = video_id
                # Save after each upload (resume-safe)
                with open(OUTPUT_FILE, "w") as f:
                    json.dump(ids, f, indent=2)
        except Exception as e:
            print(f"  ERROR uploading {key}: {e}")
            print("  Run again to retry.")
            break

    print(f"\n✓ Uploaded {len(ids)}/6 videos.")
    print(f"  IDs saved to: {OUTPUT_FILE}")

    if len(ids) == 6:
        print("\n=== Updating HTML pages ===")
        update_html_pages(ids)


def update_html_pages(ids):
    """Inject YouTube video IDs directly into the talk HTML pages."""
    import re
    talks_dir = Path.home() / "workspace-active/parvotec/Machine learning for Rupert/transcripts/talks"

    for key, ytid in ids.items():
        html_file = talks_dir / f"{key}.html"
        if not html_file.exists():
            print(f"  skip: {html_file.name} not found")
            continue
        content = html_file.read_text()
        content = re.sub(r'data-ytid="[^"]*"', f'data-ytid="{ytid}"', content)
        html_file.write_text(content)
        print(f"  ✓ {html_file.name} → {ytid}")

    print("\n  Committing...")
    os.system(
        "cd ~/workspace-active/parvotec && "
        "git add 'Machine learning for Rupert/transcripts/talks/' && "
        "git commit -m 'feat: YouTube video IDs injected (all 6 talks)' && "
        "git push origin main && git push origin main:gh-pages"
    )
    print("  ✓ Deployed.")


if __name__ == "__main__":
    main()
