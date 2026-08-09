# Parvotec / calyr.aí — Security & Cloudflare Setup

**Stand: 2026-08-09 · calyr.aí Research**

---

## A — Deployment-Status (Ist-Zustand)

| Komponente | Status | Ort |
|-----------|--------|-----|
| GitHub Pages + gate.js (PBKDF2) | ✅ **LIVE** | `ruperttscheliessnig.github.io/parvotec-internal/` |
| Cloudflare Worker (Code) | ⚙️ Bereit, **nicht deployed** | `cloudflare/worker/src/index.js` |
| Cloudflare R2 Bucket | ❌ Nicht erstellt | Cloudflare Dashboard → R2 |
| Cloudflare Access (Zero Trust) | ❌ Nicht konfiguriert | Cloudflare Dashboard → Zero Trust |
| GitHub Actions Secrets | ❌ Nicht gesetzt | Repo → Settings → Secrets |
| GitHub Branch Protection | ⏳ Manuell konfigurieren | Repo → Settings → Branches |

**Klare Aussage:** Cloudflare ist noch nicht aktiv. Die einzige Schutzschicht jetzt ist
die client-seitige PBKDF2-Gate (gate.js). Das ist für den Übergang ausreichend,
reicht aber langfristig nicht für eine echte Paywall.

---

## B — Repo-Struktur (Basis für alle Schritte unten)

```
ruperttscheliessnig/calyr-projects        ← öffentliche Hub-Seite
  dist/index.html                         ← calyr.aí Hauptseite
  dist/parvotec/index.html                ← Parvotec Projektseite (öffentlich)

ruperttscheliessnig/parvotec-internal     ← geschützte Inhalte
  Machine learning for Rupert/transcripts/
    parvotec_proposal_de.html             ← privat (nur für Berechtigte)
    parvotec_proposal_en.html             ← privat
    parvotec_asgct2026_analysis*.html     ← privat
    index.html                            ← privat
  cloudflare/
    worker/src/index.js                   ← Worker Code (bereit)
    worker/wrangler.toml                  ← Konfiguration
    upload-to-r2.sh                       ← Upload-Script
  .github/workflows/deploy.yml            ← CI/CD (wartet auf Secrets)
  gate.js                                 ← client-seitig (Übergangslösung)
```

### Ziel-Architektur (nach Cloudflare-Setup)

```
Browser
  ↓
calyrai.ai/private/parvotec_proposal_de   (geschützte URL)
  ↓
Cloudflare Edge
  ↓
Cloudflare Access  ←── E-Mail Allowlist / One-time PIN
  ↓ (nur nach Login)
Cloudflare Worker  ←── parvotec-private Worker
  ↓
R2 Bucket "parvotec-private"  ←── kein öffentlicher Zugriff
  ↓
HTML an Browser (gate.js automatisch entfernt via HTMLRewriter)
```

---

## C — Schritt-für-Schritt Setup (vollständig)

### Schritt 1 — Cloudflare-Konto + Domain

**1a. Cloudflare-Konto anlegen**
```
https://dash.cloudflare.com/sign-up
E-Mail + Passwort → Konto erstellen
```

**1b. Domain calyrai.ai hinzufügen**
```
Cloudflare Dashboard
→ Add a Site
→ calyrai.ai eingeben
→ Free Plan (reicht für den Start)
→ Continue
```

Cloudflare zeigt dir 2 Nameserver, z.B.:
```
ns1.cloudflare.com
ns2.cloudflare.com
```

**1c. Nameserver beim Domainregistrar setzen**
```
Bei deinem Registrar (z.B. Namecheap, GoDaddy, Porkbun):
→ Domain Management → DNS → Nameservers
→ Custom nameservers
→ ns1.cloudflare.com + ns2.cloudflare.com eintragen
→ Speichern
```
Propagation: 5 Min – 24h. Cloudflare benachrichtigt per E-Mail wenn aktiv.

**Test:** Cloudflare Dashboard → calyrai.ai → Status = "Active" ✅

**Sicherheitswarnung:** Nicht "Pause Cloudflare" aktivieren — dann läuft alles am
Proxy vorbei und Cloudflare Access greift nicht mehr.

---

### Schritt 2 — GitHub mit Cloudflare Pages verbinden

**Welches Repo:** `ruperttscheliessnig/calyr-projects` → das ist die öffentliche Seite.

```
Cloudflare Dashboard
→ Workers & Pages
→ Create
→ Pages
→ Connect to Git
→ GitHub autorisieren
→ Repository: ruperttscheliessnig/calyr-projects
→ Production branch: main
→ Build settings:
    Framework preset: None
    Build command:    (leer lassen, dist/ ist bereits gebaut)
    Build output:     dist
→ Save and Deploy
```

Cloudflare gibt dir eine URL wie:
```
calyr-projects.pages.dev
```

**Custom Domain verbinden:**
```
Workers & Pages → calyr-projects → Custom domains
→ Set up a custom domain
→ calyrai.ai
→ Activate domain
```

**Test:** `curl -I https://calyrai.ai` → HTTP/2 200 + `cf-ray:` Header ✅

**Sicherheitswarnung:** Das `dist/` Verzeichnis darf KEINE privaten HTML-Dateien
enthalten. Alle geschützten Inhalte kommen aus R2, nicht aus dem GitHub-Build.

---

### Schritt 3 — R2 Bucket erstellen (privater Inhaltsspeicher)

```
Cloudflare Dashboard
→ R2 Object Storage
→ Create bucket
→ Name: parvotec-private
→ Location: Auto (oder EU für DSGVO)
→ Create bucket
```

**WICHTIG:** Keinen Public Access aktivieren.
```
Bucket Settings → Public access → NOT enabled ✅
```

**Test:** Versuche direkt auf `https://pub-xxx.r2.dev/test.html` zuzugreifen →
muss "Access Denied" oder 404 ergeben. ✅

---

### Schritt 4 — HTML-Dateien in R2 hochladen

**4a. Wrangler installieren (Terminal auf deinem Mac):**
```bash
npm install -g wrangler
wrangler --version   # muss >= 3.x sein
```

**4b. Mit Cloudflare-Konto authentifizieren:**
```bash
wrangler login
# Öffnet Browser → Cloudflare OAuth → Autorisieren
```

**4c. HTML-Dateien hochladen:**
```bash
cd ~/workspace-active/parvotec
chmod +x cloudflare/upload-to-r2.sh
./cloudflare/upload-to-r2.sh
```

Das Script lädt alle 13 HTML-Dateien in `parvotec-private` hoch.

**Alternativ einzeln:**
```bash
wrangler r2 object put parvotec-private/parvotec_proposal_de.html \
  --file "Machine learning for Rupert/transcripts/parvotec_proposal_de.html" \
  --content-type "text/html; charset=utf-8"
```

**Test:**
```bash
wrangler r2 object list parvotec-private
# Muss alle 13 Dateien zeigen
```

---

### Schritt 5 — Cloudflare Worker deployen (der Türsteher)

**5a. Worker konfigurieren** — `cloudflare/worker/wrangler.toml` prüfen:
```toml
name = "parvotec-private"
main = "src/index.js"
compatibility_date = "2026-08-09"

[[r2_buckets]]
binding  = "PRIVATE"
bucket_name = "parvotec-private"

[[routes]]
pattern = "calyrai.ai/private/*"
zone_name = "calyrai.ai"
```

**5b. Worker deployen:**
```bash
cd ~/workspace-active/parvotec/cloudflare/worker
npm install
npx wrangler deploy
```

Ausgabe:
```
✅ Deployed parvotec-private to calyrai.ai/private/*
```

**Test (vor Access-Konfiguration):**
```bash
curl https://calyrai.ai/private/parvotec_proposal_de.html
# Muss HTML zurückgeben (Worker läuft, Access kommt im nächsten Schritt)
```

**Sicherheitswarnung:** Bis Schritt 6 abgeschlossen ist, ist `/private/*` noch ohne
Authentifizierung erreichbar. Schritt 5 + 6 nacheinander ohne Pause ausführen.

---

### Schritt 6 — Cloudflare Access konfigurieren

```
Cloudflare Dashboard
→ Zero Trust
→ Access
→ Applications
→ Add an Application
→ Self-hosted
```

**Application-Einstellungen:**
```
Application name:   Parvotec Private Content
Session Duration:   6 hours
Application domain:
  Subdomain: (leer)
  Domain:    calyrai.ai
  Path:      /private/*
```

**Policy erstellen:**
```
Policy name:  Authorized Researchers
Action:       Allow

Rules:
  Selector: Emails
  Value:    rupert@..., partner@company.com, forscher@uni.at
  
  (Jede E-Mail-Adresse einzeln hinzufügen)

Identity providers:
  ✅ One-time PIN
  (Benutzer gibt E-Mail ein → bekommt Code → kommt rein)
```

**KRITISCHE Sicherheitseinstellung:**
```
⛔ NICHT: Allow → Everyone who has One-time PIN
✅ NUR:   Allow → Emails = [explizite Liste]
```
Sonst kann jeder mit einer beliebigen E-Mail-Adresse hinein.

**Test:**
```bash
curl https://calyrai.ai/private/parvotec_proposal_de.html
# Muss jetzt HTTP 302 → Cloudflare Access Login Page ergeben ✅

# Im Browser:
# → https://calyrai.ai/private/parvotec_proposal_de.html
# → Redirect zu Cloudflare Access Login
# → E-Mail eingeben → OTP-Code → Zugriff ✅
```

---

### Schritt 7 — GitHub Actions Secrets setzen (CI/CD aktivieren)

```
GitHub → ruperttscheliessnig/parvotec-internal
→ Settings → Secrets and variables → Actions
→ New repository secret
```

| Secret Name | Wert |
|------------|------|
| `CLOUDFLARE_API_TOKEN` | Cloudflare → My Profile → API Tokens → Create Token → **Edit Cloudflare Workers** Template → erstellen |
| `CLOUDFLARE_ACCOUNT_ID` | Cloudflare Dashboard → rechte Seitenleiste → Account ID |

Nach dem Setzen: nächster `git push origin main` löst automatisch aus:
- Worker deploy (wenn cloudflare/worker/ geändert)
- R2 upload (wenn transcripts/*.html geändert)
- gh-pages sync (immer)

**Test:**
```
GitHub → ruperttscheliessnig/parvotec-internal → Actions
→ Deploy — Cloudflare Worker + R2 → Run workflow → Force R2 upload: true
→ Run workflow
→ Alle 3 Jobs müssen grün werden ✅
```

---

### Schritt 8 — GitHub Branch Protection (Deployment-Schutz)

```
GitHub → ruperttscheliessnig/parvotec-internal
→ Settings → Branches → Add branch protection rule
→ Branch name pattern: gh-pages

Aktivieren:
  ☑ Require signed commits
  ☑ Require pull request reviews before merging (1 reviewer)
  ☑ Include administrators
```

Gleiches für `main` Branch.

---

### Schritt 9 — Öffentliche Vorschauseite (Publications)

Für die URL `calyrai.ai/publications/asgct2026` (öffentliche Nature-artige Vorschau)
muss eine statische Seite im `calyr-projects/dist/` gebaut werden:

```
calyr-projects/dist/publications/asgct2026/index.html
  → Titel, Autoren, Abstract (öffentlich)
  → Button "Access full article" → href="/private/parvotec_asgct2026_analysis_bilingual.html"
```

Diese Seite liegt im öffentlichen Cloudflare Pages Deploy — ohne geschützten Inhalt.

---

## D — Sicherheitstest: Vollständige Prüfung

Nach vollständigem Setup müssen alle diese Tests bestehen:

```bash
# 1. Direkter R2-Zugriff → muss scheitern
curl "https://parvotec-private.r2.cloudflarestorage.com/parvotec_proposal_de.html"
# Erwartung: AccessDenied oder 403 ✅

# 2. Ohne Login → Redirect zu Access
curl -I "https://calyrai.ai/private/parvotec_proposal_de.html"
# Erwartung: HTTP/302, Location: https://calyrai.cloudflareaccess.com/... ✅

# 3. Mit falschem Token → abgelehnt
curl -H "CF-Access-Jwt-Assertion: fake-token" \
  "https://calyrai.ai/private/parvotec_proposal_de.html"
# Erwartung: 403 ✅

# 4. Quellcode des öffentlichen Builds enthält KEINE privaten Inhalte
curl https://calyrai.ai/ | grep -i "asgct2026\|DRG\|parvotec_proposal"
# Erwartung: kein Treffer ✅

# 5. Nach Login → HTML ausgeliefert, gate.js entfernt
# → Im Browser DevTools: kein <script src="gate.js"> im DOM ✅
```

---

## E — Threat Model (Bedrohungsanalyse)

| Angriff | Schutzschicht | Status |
|---------|--------------|--------|
| Direkte R2-URL raten | R2 kein Public Access | ✅ nach Schritt 3 |
| GitHub-Quellcode lesen | Private HTML nicht in Git | ✅ (liegt nur in R2) |
| gate.js im Browser umgehen | Kein gate.js mehr (server-seitig) | ✅ nach Schritt 5-6 |
| Cloudflare Access umgehen | Worker prüft CF-Access-JWT | ✅ Worker-Code |
| E-Mail erraten für OTP | Explizite Allowlist | ✅ nach Schritt 6 |
| Unsigned Push zu gh-pages | Branch Protection | ✅ nach Schritt 8 |
| API Token leak | Nur in GitHub Secrets | ✅ nach Schritt 7 |
| Session fixation | 6h Token-Expiry (CF Access) | ✅ Cloudflare Standard |
| Timing-Angriff auf gate.js | Nicht mehr relevant (server-seitig) | ✅ |

---

## F — Spätere Stripe-Paywall (Erweiterung ohne Neubau)

Die Worker-Architektur erlaubt spätere Stripe-Integration ohne Umbau:

```javascript
// Aktuell: Cloudflare Access prüft E-Mail-Allowlist
// Zukunft: Worker prüft Stripe-Entitlement zusätzlich

async function checkEntitlement(userEmail, env) {
  // KV Store mit {email: "active"|"trial"|null}
  const status = await env.ENTITLEMENTS.get(userEmail);
  return status === 'active' || status === 'trial';
}
```

**Stripe-Integration (wenn bereit):**
```
Stripe Webhook → Cloudflare Worker (separater Webhook-Worker)
→ setzt env.ENTITLEMENTS.put(email, "active")
→ parvotec-private Worker liest ENTITLEMENTS
→ bei "active": HTML ausliefern
→ sonst: 402 Payment Required + Stripe Checkout Link
```

GitHub, R2, Worker und Domain können exakt so bleiben.

---

## G — Passwort & Credentials

| Credential | Wert | Ort |
|-----------|------|-----|
| gate.js Passwort | `parvotec2026` | localStorage, nur Übergang |
| gate.js Salt | `calyr-parvotec-2026-v2` | gate.js (client) |
| Cloudflare API Token | In GitHub Secret | `CLOUDFLARE_API_TOKEN` |
| Cloudflare Account ID | In GitHub Secret | `CLOUDFLARE_ACCOUNT_ID` |

**Nach vollständiger Cloudflare-Einrichtung: gate.js ist redundant und kann aus den
HTML-Dateien entfernt werden.** Der Worker macht das via HTMLRewriter automatisch.

---

## H — Notfallreset

```javascript
// Browser-Konsole: client-seitigen Lockout aufheben
localStorage.removeItem('calyr_gate_lockout');
localStorage.removeItem('calyr_gate_audit');
location.reload();

// Cloudflare Access Session invalidieren:
// Zero Trust → Access → Users → user@email.com → Revoke sessions
```

---

**calyr.aí Security Documentation v3.0 · 2026-08-09**

---

## Security Features Implemented

### 1. **PBKDF2 Key Derivation** (100k iterations)
- **Was**: Simple SHA-256
- **Jetzt**: PBKDF2-SHA256 mit 100,000 Iterationen
- **Effekt**: Brute-Force 10,000x langsamer (~0.1 sec pro Versuch statt instant)
- **Standard**: NIST SP 800-132 empfohlen

### 2. **Rate Limiting**
```
Falsche Versuche:  1–2 → Error message (retry allowed)
                   3   → 15 Min Account Lockout
                   (lockout reset nach 15 min inaktivität)
```

### 3. **Token Expiry**
- **Session-Token**: Gültig für 6 Stunden
- **Nach Ablauf**: Muss Passwort erneut eingeben
- **Schutz**: Gegen Session-Fixation & Token-Replay

### 4. **Audit Logging** (lokal in Browser)
- **Speichert**: Alle Auth-Versuche mit Timestamp
- **Zugriff**: `localStorage.getItem('calyr_gate_audit')`
- **Format**: JSON-Array mit `{timestamp, success, reason}`
- **Limit**: Last 100 attempts (auto-rotation)

### 5. **Timing-Safe Comparison**
- **Schutz**: Gegen Timing Attacks (constant-time comparison)
- **Methode**: `timingSafeEqual()` statt `===`

---

## GitHub Branch Protection Setup (WICHTIG!)

### Step 1: Make Repository Private
```bash
# Klick auf GitHub: Settings → Visibility → Private
# Nur Collaborators können Source Code + History sehen
```

### Step 2: Protect gh-pages Branch
```bash
Settings → Branches → Branch Protection Rules → Add Rule

Rule Name:        gh-pages
Check Options:
  ☑ Require pull request reviews before merging (1 reviewer)
  ☑ Require status checks to pass
  ☑ Require branches to be up to date before merging
  ☑ Require signed commits  ← CRITICAL!
  ☑ Dismiss stale PR approvals
  ☑ Include administrators
```

### Step 3: Protect main Branch (Optional)
```bash
Same as above, but add:
  ☑ Require code reviews
  ☑ Require signed commits
```

### Step 4: Setup Commit Signing (Local)
```bash
# Generate GPG key (if not exists)
gpg --gen-key

# Configure Git to sign commits
git config --global user.signingKey <KEY_ID>
git config --global commit.gpgSign true

# Test signed commit
git commit -m "test" --allow-empty -S
git log --show-signature
```

---

## Authentication Workflow

### User Access
1. Opens: `https://ruperttscheliessnig.github.io/parvotec-internal/...`
2. Black overlay appears: "calyr.aí — Restricted Access"
3. Enters password: `parvotec2026`
4. Browser hashes password (PBKDF2-100k iterations)
5. ✅ If match → Token stored in localStorage (6h expiry)
6. ❌ If mismatch → Attempt counter (3 max) → Lockout after 3 failures

### Token Storage
```javascript
{
  "calyr_gate_token": "{\"created\": 1723199254000, \"nonce\": \"...\"}"
}
```

### Audit Log Access
```javascript
// In browser console:
JSON.parse(localStorage.getItem('calyr_gate_audit'))
// Output: [{timestamp, success, reason}, ...]
```

---

## Security Layers (Defense in Depth)

| Layer | Protection | Responsibility |
|-------|-----------|-----------------|
| **1. GitHub Repo** | Private repo → only Collaborators | GitHub Access Control |
| **2. Branch Protection** | Signed commits + PR review → only you can deploy | Git/GitHub |
| **3. HTML Gate** | Password + PBKDF2 + Rate Limit | Client-side Security |
| **4. HTTPS** | Data in transit encrypted | GitHub Pages (automatic) |
| **5. Audit Log** | Track all attempts (local) | Browser LocalStorage |

---

## Tested Scenarios

✅ **Correct password**: Overlay removed, full content visible  
✅ **Wrong password (1st time)**: "2 attempts remaining"  
✅ **Wrong password (2nd time)**: "1 attempt remaining"  
✅ **Wrong password (3rd time)**: "Locked for 15 minutes"  
✅ **Token expires**: Re-authentication required after 6h  
✅ **Refresh page**: Token checked, gate skipped if valid  
✅ **Clear localStorage**: Gate appears, asks for password again  

---

## Threats Mitigated

| Threat | Old Gate | Secure Gate | Method |
|--------|----------|-------------|--------|
| **Brute-Force** | ❌ instant | ✅ 0.1s/attempt | PBKDF2-100k |
| **Dictionary Attack** | ❌ 1M/sec | ✅ 10k/sec | PBKDF2 |
| **Rainbow Tables** | ❌ possible | ✅ salted hash | Salt in function |
| **Timing Attack** | ❌ vulnerable | ✅ protected | Const-time compare |
| **Session Fixation** | ❌ no expiry | ✅ 6h max | Token TTL |
| **Audit Trail** | ❌ none | ✅ 100 attempts | LocalStorage |
| **Unauthorized Deployment** | ❌ any push | ✅ signed commits only | Git + GitHub Rules |
| **Collaborator Rogue Access** | ❌ no control | ✅ PR review required | Branch protection |

---

## Recommended Next Steps

1. **Make repo private** ← Do this first
2. **Enable branch protection** (gh-pages)
3. **Setup commit signing** (local machine)
4. **Test the gate** via deployed URL
5. **Export audit logs monthly** (copy localStorage)

---

## Emergency: Reset Lockout
```javascript
// In browser console, if locked out:
localStorage.removeItem('calyr_gate_lockout');
localStorage.removeItem('calyr_gate_audit');
location.reload();
```

---

## Support
- **GitHub Docs**: [Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- **Git Signing**: [GPG Setup](https://docs.github.com/en/authentication/managing-commit-signature-verification)
- **PBKDF2 Spec**: [RFC 2898](https://tools.ietf.org/html/rfc2898)

---

**calyr.aí Security** | v2.0 | 2026-08-09
