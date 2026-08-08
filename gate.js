/* calyr.aí — access gate, SHA-256 checked via WebCrypto */
document.addEventListener('DOMContentLoaded', function () {
(function () {
  const HASH = 'ad98ac78e6fa16ff7fa4e3498e8a00f965fb725ce3aa56a47f18892b903fe010';
  const SALT = 'calyr-gate-v1';
  const KEY  = 'calyr_gate_ok';

  if (localStorage.getItem(KEY) === HASH) return;

  document.addEventListener('DOMContentLoaded', function () {
  const CSS = `
      position:fixed;inset:0;z-index:99999;
      background:#050505;display:flex;align-items:center;justify-content:center;
      font-family:'Helvetica Neue',Helvetica,Arial,sans-serif;
    }
    #cg-box {
      text-align:center;max-width:340px;width:90%;
    }
    #cg-logo {
      font-size:1.05rem;letter-spacing:-.04em;color:#fff;font-weight:400;
      margin-bottom:.35rem;
    }
    #cg-sub {
      font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;
      color:#444;margin-bottom:2rem;
    }
    #cg-input {
      width:100%;background:#0a0a0a;border:1px solid #2a2a2a;
      color:#e0e0de;font-size:.95rem;padding:.65rem .9rem;
      outline:none;text-align:center;letter-spacing:.05em;
      font-family:monospace;margin-bottom:.75rem;
    }
    #cg-input:focus { border-color:#39bfff; }
    #cg-btn {
      width:100%;background:#39bfff;color:#000;border:none;
      font-size:.72rem;font-weight:700;letter-spacing:.14em;
      text-transform:uppercase;padding:.6rem;cursor:pointer;
      font-family:inherit;
    }
    #cg-btn:hover { background:#fff; }
    #cg-err {
      font-size:.68rem;color:#f87171;letter-spacing:.06em;
      margin-top:.6rem;min-height:1.2em;
    }
  `;

  const el = document.createElement('div');
  el.id = 'cg-overlay';
  el.innerHTML = `
    <style>${CSS}</style>
    <div id="cg-box">
      <div id="cg-logo">calyr.aí</div>
      <div id="cg-sub">Restricted Access</div>
      <input id="cg-input" type="password" placeholder="Access code" autocomplete="current-password">
      <button id="cg-btn">Enter</button>
      <div id="cg-err"></div>
    </div>`;
  document.body.appendChild(el);

  const inp = document.getElementById('cg-input');
  const btn = document.getElementById('cg-btn');
  const err = document.getElementById('cg-err');

  inp.focus();

  async function check() {
    const pw = inp.value.trim();
    if (!pw) return;
    const buf = await crypto.subtle.digest(
      'SHA-256',
      new TextEncoder().encode(pw + SALT)
    );
    const hash = Array.from(new Uint8Array(buf))
      .map(b => b.toString(16).padStart(2, '0')).join('');
    if (hash === HASH) {
      localStorage.setItem(KEY, HASH);
      document.getElementById('cg-overlay').remove();
    } else {
      err.textContent = 'Incorrect code.';
      inp.value = '';
      inp.focus();
    }
  }

  btn.addEventListener('click', check);
  inp.addEventListener('keydown', e => { if (e.key === 'Enter') check(); });
})();
});
