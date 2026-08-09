/* calyr.aí — access gate, SHA-256 checked via WebCrypto */
document.addEventListener('DOMContentLoaded', function () {
  const HASH = 'ad98ac78e6fa16ff7fa4e3498e8a00f965fb725ce3aa56a47f18892b903fe010';
  const SALT = 'calyr-gate-v1';
  const KEY  = 'calyr_gate_ok';

  if (localStorage.getItem(KEY) === HASH) return;

  const overlay = document.createElement('div');
  overlay.id = 'cg-overlay';
  overlay.innerHTML = `
    <div class="cg-modal">
      <h2>calyr.aí — Restricted Access</h2>
      <p>Password required:</p>
      <input type="password" id="cg-input" placeholder="Enter password" />
      <button id="cg-submit">Unlock</button>
    </div>
  `;
  overlay.style.cssText = `
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: #111; display: flex; align-items: center; justify-content: center;
    z-index: 999999;
  `;
  const modal = overlay.querySelector('.cg-modal');
  modal.style.cssText = `
    background: #222; color: #fff; padding: 2rem; border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.8); text-align: center; max-width: 400px;
  `;
  modal.querySelectorAll('input, button').forEach(el => {
    el.style.cssText = `
      width: 100%; margin: 0.5rem 0; padding: 0.75rem; font-size: 1rem;
      border: 1px solid #555; border-radius: 4px; background: #333; color: #fff;
    `;
    el.style.boxSizing = 'border-box';
  });

  document.body.appendChild(overlay);

  const inp = document.getElementById('cg-input');
  const btn = document.getElementById('cg-submit');

  const check = async () => {
    const pwd = inp.value;
    const encoder = new TextEncoder();
    const data = encoder.encode(pwd + SALT);
    const hashBuf = await crypto.subtle.digest('SHA-256', data);
    const hashHex = Array.from(new Uint8Array(hashBuf))
      .map(b => b.toString(16).padStart(2, '0')).join('');
    if (hashHex === HASH) {
      localStorage.setItem(KEY, HASH);
      overlay.remove();
    } else {
      inp.value = '';
      inp.placeholder = 'Incorrect password';
      inp.style.borderColor = '#f00';
    }
  };

  btn.addEventListener('click', check);
  inp.addEventListener('keydown', e => { if (e.key === 'Enter') check(); });
  inp.focus();
});
