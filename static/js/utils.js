// --- toast notifications -------------------------------------------------

function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const icon = type === 'success' ? '✓' : '✕';
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${icon}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// --- confirm modal -------------------------------------------------------

let confirmCallback = null;

function showConfirm(title, text, onConfirm) {
  document.getElementById('confirmTitle').textContent = title;
  document.getElementById('confirmText').textContent = text;
  confirmCallback = onConfirm;
  document.getElementById('confirmModal').classList.add('visible');
}

function closeConfirm() {
  document.getElementById('confirmModal').classList.remove('visible');
  confirmCallback = null;
}

document.getElementById('confirmBtn').addEventListener('click', () => {
  if (confirmCallback) confirmCallback();
  closeConfirm();
});

document.getElementById('confirmModal').addEventListener('click', (e) => {
  if (e.target === e.currentTarget) closeConfirm();
});

// --- api helper ----------------------------------------------------------

async function api(method, url, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) opts.body = JSON.stringify(body);

  const res = await fetch(url, opts);
  const data = await res.json();
  return { ok: res.ok, status: res.status, data };
}

// --- show field errors from API response ---------------------------------

function showErrors(errors, formEl = document) {
  // clear previous errors
  formEl.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  formEl.querySelectorAll('.invalid-feedback').forEach(el => el.textContent = '');

  const errorList = formEl.querySelector('.error-list');
  if (errorList) {
    const ul = errorList.querySelector('ul');
    ul.innerHTML = '';
    errors.forEach(e => {
      const label = e.field ? `${e.field}: ${e.message}` : e.message;
      ul.innerHTML += `<li>${label}</li>`;
    });
    errorList.classList.add('visible');
  }
}

function clearErrors(formEl = document) {
  formEl.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  const errorList = formEl.querySelector('.error-list');
  if (errorList) errorList.classList.remove('visible');
}