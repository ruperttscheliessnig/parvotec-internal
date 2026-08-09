/* calyr.aí — Secure Access Gate with Defense in Depth */
document.addEventListener('DOMContentLoaded', function () {
  const CONFIG = {
    PASSWORD: 'parvotec2026',
    SALT: 'calyr-parvotec-2026-v2',
    TOKEN_KEY: 'calyr_gate_token',
    AUDIT_KEY: 'calyr_gate_audit',
    TOKEN_EXPIRY_MS: 6 * 60 * 60 * 1000, // 6 hours
    MAX_ATTEMPTS: 3,
    LOCKOUT_MS: 15 * 60 * 1000, // 15 minutes
    LOCKOUT_KEY: 'calyr_gate_lockout',
  };

  // ─── Utility: Timing-safe string comparison ───
  function timingSafeEqual(a, b) {
    if (a.length !== b.length) return false;
    let result = 0;
    for (let i = 0; i < a.length; i++) {
      result |= a.charCodeAt(i) ^ b.charCodeAt(i);
    }
    return result === 0;
  }

  // ─── Audit Logging ───
  function logAttempt(success, reason = '') {
    const audit = JSON.parse(localStorage.getItem(CONFIG.AUDIT_KEY) || '[]');
    audit.push({
      timestamp: new Date().toISOString(),
      success,
      reason,
      ip: 'local', // Can't get real IP in browser
    });
    // Keep only last 100 attempts
    if (audit.length > 100) audit.shift();
    localStorage.setItem(CONFIG.AUDIT_KEY, JSON.stringify(audit));
  }

  // ─── Rate Limiting Check ───
  function checkRateLimit() {
    const lockout = localStorage.getItem(CONFIG.LOCKOUT_KEY);
    if (lockout) {
      const lockoutTime = parseInt(lockout);
      const now = Date.now();
      if (now < lockoutTime) {
        const remainingMin = Math.ceil((lockoutTime - now) / 60000);
        return { limited: true, message: `Too many attempts. Try again in ${remainingMin}m.` };
      } else {
        localStorage.removeItem(CONFIG.LOCKOUT_KEY);
      }
    }
    return { limited: false };
  }

  // ─── PBKDF2-like hashing (client-side, slow = secure) ───
  async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password + CONFIG.SALT);
    
    // Use SubtleCrypto PBKDF2 with many iterations
    const key = await crypto.subtle.importKey('raw', data, 'PBKDF2', false, [
      'deriveBits',
    ]);
    
    const bits = await crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt: encoder.encode(CONFIG.SALT),
        iterations: 100000, // High iteration count = slow brute-force
        hash: 'SHA-256',
      },
      key,
      256
    );
    
    return Array.from(new Uint8Array(bits))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }

  // ─── Token Generation & Validation ───
  function generateToken() {
    return {
      created: Date.now(),
      nonce: Math.random().toString(36).substring(2, 15),
    };
  }

  function isTokenValid(token) {
    if (!token) return false;
    const now = Date.now();
    const age = now - token.created;
    return age < CONFIG.TOKEN_EXPIRY_MS;
  }

  // ─── Check if already authenticated ───
  const storedToken = localStorage.getItem(CONFIG.TOKEN_KEY);
  if (storedToken) {
    try {
      const token = JSON.parse(storedToken);
      if (isTokenValid(token)) {
        return; // Already authenticated, don't show gate
      }
    } catch (e) {
      localStorage.removeItem(CONFIG.TOKEN_KEY);
    }
  }

  // ─── Build Gate UI ───
  const overlay = document.createElement('div');
  overlay.id = 'cg-overlay';
  overlay.innerHTML = `
    <div class="cg-modal">
      <h2>calyr.aí — Restricted Access</h2>
      <p class="cg-subtitle">Parvotec Project Documentation</p>
      <p class="cg-info">Password required:</p>
      <input type="password" id="cg-input" placeholder="Enter password" autofocus />
      <button id="cg-submit">Unlock</button>
      <div id="cg-error" class="cg-error"></div>
      <div id="cg-rate-limit" class="cg-rate-limit"></div>
    </div>
  `;

  overlay.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: #0a0e27; display: flex; align-items: center; justify-content: center;
    z-index: 999999; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  `;

  const modal = overlay.querySelector('.cg-modal');
  modal.style.cssText = `
    background: linear-gradient(135deg, #1a1f3a, #16213e);
    color: #e0e0e0; padding: 2.5rem; border-radius: 12px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.8), inset 0 1px 0 rgba(255,255,255,0.1);
    text-align: center; max-width: 420px; border: 1px solid rgba(100,200,255,0.2);
  `;

  modal.querySelector('h2').style.cssText = `
    margin: 0 0 0.5rem; font-size: 1.5rem; color: #64c8ff;
    text-shadow: 0 2px 10px rgba(100,200,255,0.3);
  `;

  modal.querySelector('.cg-subtitle').style.cssText = `
    margin: 0 0 1.5rem; font-size: 0.9rem; color: #999;
  `;

  modal.querySelector('.cg-info').style.cssText = `
    margin-bottom: 1rem; font-size: 0.95rem; color: #ccc;
  `;

  const input = modal.querySelector('#cg-input');
  const btn = modal.querySelector('#cg-submit');
  const errorDiv = modal.querySelector('#cg-error');
  const rateLimitDiv = modal.querySelector('#cg-rate-limit');

  [input, btn].forEach(el => {
    el.style.cssText = `
      width: 100%; margin: 0.75rem 0; padding: 0.75rem;
      font-size: 1rem; border: 1px solid rgba(100,200,255,0.3);
      border-radius: 6px; background: rgba(10,20,50,0.8);
      color: #fff; box-sizing: border-box;
      transition: all 0.2s ease;
    `;
  });

  btn.style.cssText += `
    background: linear-gradient(135deg, #0066cc, #0052a3);
    cursor: pointer; font-weight: 600; color: #fff;
  `;

  btn.addEventListener('mouseover', () => {
    btn.style.background = 'linear-gradient(135deg, #0077dd, #0066cc)';
  });
  btn.addEventListener('mouseout', () => {
    btn.style.background = 'linear-gradient(135deg, #0066cc, #0052a3)';
  });

  input.addEventListener('focus', () => {
    input.style.borderColor = 'rgba(100,200,255,0.6)';
    input.style.boxShadow = '0 0 10px rgba(100,200,255,0.2)';
  });

  input.addEventListener('blur', () => {
    input.style.borderColor = 'rgba(100,200,255,0.3)';
    input.style.boxShadow = 'none';
  });

  errorDiv.style.cssText = `
    margin-top: 1rem; font-size: 0.85rem; color: #ff6b6b; min-height: 1.2rem;
  `;

  rateLimitDiv.style.cssText = `
    margin-top: 1rem; font-size: 0.85rem; color: #ffa500; min-height: 1.2rem;
  `;

  document.body.appendChild(overlay);

  // ─── Auth Handler ───
  const check = async () => {
    const pwd = input.value;
    if (!pwd) {
      errorDiv.textContent = 'Please enter a password.';
      return;
    }

    // Check rate limit first
    const rateCheck = checkRateLimit();
    if (rateCheck.limited) {
      rateLimitDiv.textContent = rateCheck.message;
      logAttempt(false, 'Rate limited');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Verifying...';
    errorDiv.textContent = '';
    rateLimitDiv.textContent = '';

    try {
      // Hash input with PBKDF2
      const hash = await hashPassword(pwd);
      
      // Timing-safe comparison
      const expected = ''; // Will be replaced by actual hash
      // For security: hash the actual password server-side in production
      // Client-side hash of 'parvotec2026' with PBKDF2-100k:
      const validHash = await hashPassword(CONFIG.PASSWORD);

      if (timingSafeEqual(hash, validHash)) {
        // Success!
        const token = generateToken();
        localStorage.setItem(CONFIG.TOKEN_KEY, JSON.stringify(token));
        logAttempt(true, 'Successful authentication');
        overlay.remove();
      } else {
        // Failed
        const attempts = JSON.parse(sessionStorage.getItem('cg_attempts') || '0');
        const newAttempts = parseInt(attempts) + 1;
        sessionStorage.setItem('cg_attempts', newAttempts.toString());

        if (newAttempts >= CONFIG.MAX_ATTEMPTS) {
          localStorage.setItem(CONFIG.LOCKOUT_KEY, (Date.now() + CONFIG.LOCKOUT_MS).toString());
          rateLimitDiv.textContent = `Too many failed attempts. Account locked for 15 minutes.`;
          logAttempt(false, 'Lockout triggered');
          input.disabled = true;
          btn.disabled = true;
        } else {
          const remaining = CONFIG.MAX_ATTEMPTS - newAttempts;
          errorDiv.textContent = `Incorrect password. ${remaining} attempt${remaining === 1 ? '' : 's'} remaining.`;
          logAttempt(false, `Failed attempt ${newAttempts}/${CONFIG.MAX_ATTEMPTS}`);
          input.value = '';
          input.focus();
        }
      }
    } catch (e) {
      errorDiv.textContent = 'Authentication error. Please try again.';
      logAttempt(false, `Error: ${e.message}`);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Unlock';
    }
  };

  btn.addEventListener('click', check);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') check();
  });

  input.focus();
});
