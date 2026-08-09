# PARVOTEC — Project Documentation
**Repo:** `ruperttscheliessnig/parvotec-internal`  
**Live:** `ruperttscheliessnig.github.io/parvotec-internal/` (GitHub Pages, gate.js-geschützt)  
**Ziel:** Wissenschaftliche Dokumentationsplattform für das PARVOTEC-Forschungsprojekt (AAV-Kapside, ML-gestütztes Design, Förderprojekt-Proposals)

---

## Inhalt

### Kernmaterial
| Ordner / Datei | Beschreibung |
|---|---|
| `Machine learning for Rupert/` | Alle Primärquellen: PDFs, Abstracts, Transkripte |
| `Machine learning for Rupert/ASGCT2026/` | 6 MP4-Videos (~7.3 GB) — ASGCT 2026 Talks |
| `Machine learning for Rupert/transcripts/` | HTML-Berichte, Transkripte (.txt, .wav, .vtt), Proposals |
| `Machine learning for Rupert/transcripts/talks/` | 6 HTML-Seiten mit YouTube-Embed (IDs noch `PENDING`) |
| `data/` | YAML-Specs: Workstation, AORTA, DRG, Scientific Node |

### Proposals
| Datei | Inhalt |
|---|---|
| `transcripts/parvotec_proposal_de.html` | Phase I (12 AT, WP1–7) + Hauptprojekt (12 M, OWP1–8), DE |
| `transcripts/parvotec_proposal_en.html` | Englische Version desselben Proposals |
| `transcripts/parvotec_aorta_proposal.html` | AORTA-spezifischer Antrag |

### Analyse-Berichte (HTML)
| Datei | Inhalt |
|---|---|
| `parvotec_asgct2026_analysis.html` | ASGCT 2026 Zusammenfassung |
| `parvotec_asgct2026_analysis_bilingual.html` | Zweisprachige Version |
| `AAV_Capsid_Analytics_Strategy_Report.html` | Strategie-Report AAV Capsid Analytics |
| `parvotec_app_biophysics.html` | Biophysik-Antrag |
| `parvotec_app_computational.html` | Computational-Antrag |
| `parvotec_scientific_node.html` | Scientific Node Workstation |

---

## Scripts

| Script | Zweck |
|---|---|
| `transcribe_all.py` | Whisper-Transkription aller MP4s → .txt + .wav |
| `extract_pptx_ocr.py` | OCR aus PPTX-Folien via Tesseract |
| `upload_to_youtube.py` | OAuth2 Upload → YouTube (unlisted), injiziert IDs in HTML |
| `update_youtube_ids.sh` | Manuelles Setzen von YouTube-IDs in HTML-Dateien |
| `build.py` / `build_workstation.py` | YAML → HTML-Spezifikationen |
| `build_specifications.py` | Spezifikations-Builder |
| `run_video_analysis.sh` | Video-Analyse-Pipeline |

---

## Sicherheit

### Aktuell live (GitHub Pages)
- **gate.js** — PBKDF2-SHA256 (100k Iterationen), Rate Limiting (3 Versuche → 15 min Sperre), 6h Token, Audit-Log
- Passwort: `parvotec2026` · Salt: `calyr-parvotec-2026-v2`
- **Schwäche:** Client-seitig — ersetzbar durch Cloudflare Access

### Geplant (Cloudflare)
- **Worker** (`cloudflare/worker/src/index.js`) — R2-Proxy, HTMLRewriter entfernt gate.js
- **R2 Bucket** `parvotec-private` — alle HTML-Dateien, kein öffentlicher Zugriff
- **GitHub Actions** (`.github/workflows/deploy.yml`) — Auto-Deploy bei Push
- **Fehlend:** Cloudflare Billing (für R2), GitHub Secrets, `wrangler deploy`

---

## YouTube Upload (ausstehend)

```bash
# Voraussetzung: client_secrets.json von Google Cloud herunterladen
# Projekt: gcal-automation-478305
# OAuth2 Client-ID: 953163789760-5glsqc7skuk33u33um1km61g6i7a4mug.apps.googleusercontent.com

cd ~/workspace-active/parvotec
~/miniforge3/bin/python3 upload_to_youtube.py
# Browser öffnet sich → Google-Login → autorisieren
# → 6 Videos werden als "unlisted" hochgeladen
# → IDs werden automatisch in HTML injiziert + git push
```

**Videos:**
| Datei | Talk |
|---|---|
| `AAV_Engineering_III.mp4` | AAV Engineering III |
| `AAV_Engineering_IV.mp4` | AAV Engineering IV |
| `AAV_Trafficking.mp4` | AAV Trafficking |
| `Lir_AAV_LLM.mp4` | LLM für AAV (Lir) |
| `ShapeTX_AAV5engineering.mp4` | ShapeTX AAV5 Engineering |
| `TuningReceptorInteractions_Caltech.mp4` | Receptor Interactions (Caltech) |

---

## Git History (aktuell)

```
2bb605c  feat: YouTube upload script (OAuth2 + auto HTML inject + git push)
56a22ee  feat: YouTube embed player in all 6 talk pages (IDs pending upload)
d7824e2  docs: Cloudflare setup guide + security status
44352dd  ci: GitHub Actions — Worker deploy + R2 upload + gh-pages sync
a0cb7e5  feat: Cloudflare Worker + R2 paywall
2064df5  feat: bilingual proposal DE+EN (Phase I + 12M Oracle)
9e31a5d  security: PBKDF2, rate limiting, token expiry, audit logging
```

---

## Nächste Schritte

1. `client_secrets.json` herunterladen → Google Cloud Console → gcal-automation-478305
2. `upload_to_youtube.py` ausführen → 6 Videos hochladen
3. Cloudflare Billing aktivieren → R2 Bucket `parvotec-private` erstellen
4. GitHub Secrets setzen: `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID`
5. `wrangler deploy` → Worker live schalten
6. Cloudflare Access konfigurieren → gate.js entfernen

---

## Deployment-Ziel (Cloudflare)

```
ruperttscheliessnig/parvotec-internal  (privat)
              │
              ▼
    Cloudflare Pages / Worker
              │
    parvotec.calyrai.ai  ← Cloudflare Access (E-Mail-Allowlist)
              │
         R2 Bucket  ← private HTML-Dateien
         Stream     ← private Videos (alternativ zu YouTube)
```
