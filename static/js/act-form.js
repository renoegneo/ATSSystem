// --- row management -------------------------------------------------------

function addRow(table, data = {}) {
  const tbody = document.getElementById(`${table}Tbody`);
  const rowNum = tbody.rows.length + 1;
  const tr = document.createElement('tr');
  tr.dataset.table = table;

  tr.innerHTML = `
    <td>${rowNum}</td>
    <td><input type="text"   class="name-input"  placeholder="Наименование" value="${data.name     || ''}"></td>
    <td><input type="number" class="price-input" placeholder="0" min="0.01" step="0.01" value="${data.price    || ''}"></td>
    <td><input type="number" class="qty-input"   placeholder="1" min="0.01" step="0.01" value="${data.quantity || ''}"></td>
    <td><span class="amount-cell">${data.amount ? fmt(data.amount) : '—'}</span></td>
    <td>
      <button type="button" onclick="removeRow(this)"
        style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:16px;padding:4px 6px;">
        <i class="bi bi-x"></i>
      </button>
    </td>
  `;

  tr.querySelector('.price-input').addEventListener('input', () => recalcRow(tr));
  tr.querySelector('.qty-input').addEventListener('input',   () => recalcRow(tr));

  // Enter → move to next input or add new row
  const inputs = tr.querySelectorAll('input');
  inputs.forEach((inp, idx) => {
    inp.addEventListener('keydown', (e) => {
      if (e.key !== 'Enter') return;
      e.preventDefault();
      if (idx < inputs.length - 1) {
        inputs[idx + 1].focus();
      } else {
        addRow(table);
        document.getElementById(`${table}Tbody`).lastElementChild.querySelector('.name-input').focus();
      }
    });
  });

  tbody.appendChild(tr);
  recalcTable(table);
  saveDraft();
}

function removeRow(btn) {
  const tr = btn.closest('tr');
  const table = tr.dataset.table;
  tr.remove();
  renumberRows(table);
  recalcTable(table);
  saveDraft();
}

function renumberRows(table) {
  Array.from(document.getElementById(`${table}Tbody`).rows).forEach((tr, i) => {
    tr.cells[0].textContent = i + 1;
  });
}

// --- calculations ---------------------------------------------------------

function fmt(n) {
  return Number(n).toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function recalcRow(tr) {
  const price = parseFloat(tr.querySelector('.price-input').value) || 0;
  const qty   = parseFloat(tr.querySelector('.qty-input').value)   || 1;
  tr.querySelector('.amount-cell').textContent = price > 0 ? fmt(price * qty) : '—';
  recalcTable(tr.dataset.table);
  saveDraft();
}

function recalcTable(table) {
  let total = 0;
  Array.from(document.getElementById(`${table}Tbody`).rows).forEach(tr => {
    const price = parseFloat(tr.querySelector('.price-input').value) || 0;
    const qty   = parseFloat(tr.querySelector('.qty-input').value)   || 1;
    total += price * qty;
  });
  document.getElementById(`${table}TotalCell`).textContent = fmt(total);
  recalcGrand();
}

function recalcGrand() {
  const p = parseFloat(document.getElementById('partsTotalCell').textContent.replace(/\s/g,'').replace(',','.')) || 0;
  const w = parseFloat(document.getElementById('worksTotalCell').textContent.replace(/\s/g,'').replace(',','.')) || 0;
  document.getElementById('grandTotal').textContent = fmt(p + w);
}

// --- draft ----------------------------------------------------------------

const DRAFT_KEY = 'act_draft';

function saveDraft() {
  localStorage.setItem(DRAFT_KEY, JSON.stringify(collectFormData()));
}

function loadDraft() {
  const raw = localStorage.getItem(DRAFT_KEY);
  if (!raw) return false;
  try {
    const d = JSON.parse(raw);
    if (d.act_date)     document.getElementById('actDate').value     = d.act_date;
    if (d.car_info)     document.getElementById('carInfo').value     = d.car_info;
    if (d.driver_name)  document.getElementById('driverName').value  = d.driver_name;
    if (d.driver_phone) document.getElementById('driverPhone').value = d.driver_phone;
    if (d.boss_phone)   document.getElementById('bossPhone').value   = d.boss_phone;

    document.getElementById('partsTbody').innerHTML = '';
    document.getElementById('worksTbody').innerHTML = '';

    (d.parts?.length ? d.parts : [{}]).forEach(r => addRow('parts', r));
    (d.works?.length ? d.works : [{}]).forEach(r => addRow('works', r));
    return true;
  } catch (_) { return false; }
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY);
}

// --- collect --------------------------------------------------------------

function collectFormData() {
  const rows = (tbodyId) =>
    Array.from(document.getElementById(tbodyId).rows)
      .map(tr => ({
        name:     tr.querySelector('.name-input').value.trim(),
        price:    parseFloat(tr.querySelector('.price-input').value) || null,
        quantity: parseFloat(tr.querySelector('.qty-input').value)   || 1,
      }))
      .filter(r => r.name || r.price);  // skip fully empty rows

  return {
    act_date:     document.getElementById('actDate').value,
    car_info:     document.getElementById('carInfo').value.trim(),
    driver_name:  document.getElementById('driverName').value.trim()  || null,
    driver_phone: document.getElementById('driverPhone').value.trim() || null,
    boss_phone:   document.getElementById('bossPhone').value.trim()   || null,
    parts: rows('partsTbody'),
    works: rows('worksTbody'),
  };
}

// --- submit helpers (called from each page, not registered here) ----------

async function submitCreate() {
  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="bi bi-hourglass"></i> Сохранение...';
  clearErrors();

  const { ok, data } = await api('POST', '/acts/api', collectFormData());

  if (ok) {
    clearDraft();
    showToast('Акт успешно сохранён');
    setTimeout(() => { window.location.href = `/acts/${data.id}`; }, 800);
  } else {
    showErrors(data.errors || [{ field: '', message: 'Неизвестная ошибка' }]);
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-check-lg"></i> Сохранить акт';
  }
}

async function submitUpdate(actId) {
  const btn = document.getElementById('submitBtn');
  btn.disabled = true;
  btn.innerHTML = '<i class="bi bi-hourglass"></i> Сохранение...';
  clearErrors();

  const { ok, data } = await api('PUT', `/acts/api/${actId}`, collectFormData());

  if (ok) {
    showToast('Изменения сохранены');
    setTimeout(() => { window.location.href = `/acts/${actId}`; }, 800);
  } else {
    showErrors(data.errors || [{ field: '', message: 'Неизвестная ошибка' }]);
    btn.disabled = false;
    btn.innerHTML = '<i class="bi bi-check-lg"></i> Сохранить изменения';
  }
}

// --- attach header input draft saving ------------------------------------

function initDraftListeners() {
  ['actDate','carInfo','driverName','driverPhone','bossPhone'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', saveDraft);
  });
}

// showErrors / clearErrors wrappers that default to the page's error list
function showErrors(errors) {
  const list = document.getElementById('errorList');
  if (!list) return;
  const ul = list.querySelector('ul');
  ul.innerHTML = '';
  errors.forEach(e => {
    ul.innerHTML += `<li>${e.field ? e.field + ': ' : ''}${e.message}</li>`;
  });
  list.classList.add('visible');
}

function clearErrors() {
  document.getElementById('errorList')?.classList.remove('visible');
}