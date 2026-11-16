const $ = selector => document.querySelector(selector);
const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let state, mode = 'deposit', busy = false, timer;
const symbols = {USD:'$',GBP:'£',EURO:'€',CFA:'F'};
const names = {USD:'US Dollar',GBP:'British Pound',EURO:'Euro',CFA:'CFA Franc'};
const number = value => Number(value).toLocaleString('en-GB',{minimumFractionDigits:2,maximumFractionDigits:2});

async function api(path,data) {
  let response;
  try { response = await fetch(path,data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); }
  catch { throw new Error('The local wallet is offline. Start its server and refresh.'); }
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'That transaction could not be completed.');
  return result;
}

function toast(message) {
  clearTimeout(timer); $('#toast').textContent = message; $('#toast').hidden = false;
  timer = setTimeout(() => { $('#toast').hidden = true; },6500);
}

function quote() {
  if (!state) return;
  const rate = Number(state.currencies.find(item => item.code === $('#currency').value).rate);
  const amount = $('#full-withdraw').checked ? Number(state.balance) : Number($('#amount').value) * rate;
  $('#quote').textContent = `GH₵ ${number(Number.isFinite(amount) && amount > 0 ? amount : 0)}`;
}

function render() {
  $('#balance').textContent = number(state.balance);
  $('#currency-grid').innerHTML = state.currencies.filter(item => item.code !== 'GHS').map(item => `<article class="currency-card"><span class="currency-symbol">${symbols[item.code]}</span><div><strong>${item.code === 'EURO' ? 'EUR' : item.code}</strong><span>${names[item.code]}</span></div><b>${number(item.balance)}</b></article>`).join('');
  $('#rate-list').innerHTML = state.currencies.filter(item => item.code !== 'GHS').map(item => `<div><span>1 ${item.code === 'EURO' ? 'EUR' : item.code}</span><strong>GHS ${escapeHtml(item.rate)}</strong></div>`).join('');
  $('#activity-count').textContent = `${state.history.length} ${state.history.length === 1 ? 'transaction' : 'transactions'}`;
  if (state.history.length) {
    $('#activity-content').innerHTML = `<div class="table-scroll"><table><thead><tr><th>Transaction</th><th>Original amount</th><th>GHS change</th><th>Balance after</th></tr></thead><tbody>${state.history.map(item => `<tr><td><span class="activity-icon ${item.kind === 'deposit' ? 'in' : 'out'}">${item.kind === 'deposit' ? '↓' : '↗'}</span><span><strong>${item.kind === 'deposit' ? 'Deposit' : item.kind === 'withdraw_all' ? 'Full withdrawal' : 'Withdrawal'}</strong><small>${escapeHtml(item.time)}</small></span></td><td>${escapeHtml(item.currency)} ${number(item.amount)}</td><td class="${item.kind === 'deposit' ? 'positive' : ''}">${item.kind === 'deposit' ? '+' : '−'} ${number(item.ghs)}</td><td>GH₵ ${number(item.balance)}</td></tr>`).join('')}</tbody></table></div>`;
  }
  quote();
}

function setMode(next) {
  mode = next; $('#deposit-tab').classList.toggle('active',mode === 'deposit'); $('#withdraw-tab').classList.toggle('active',mode === 'withdraw');
  $('#deposit-tab').setAttribute('aria-pressed',String(mode === 'deposit')); $('#withdraw-tab').setAttribute('aria-pressed',String(mode === 'withdraw'));
  $('#full-withdraw-label').hidden = mode !== 'withdraw'; $('#full-withdraw').checked = false; $('#amount').disabled = false; $('#amount').required = true;
  $('#submit-transaction').innerHTML = `${mode === 'deposit' ? 'Add to wallet' : 'Withdraw from wallet'} <span>↗</span>`;
  $('#form-error').textContent = ''; quote();
}

async function transact(payload) {
  if (busy) return;
  busy = true; $('#submit-transaction').disabled = true; $('#form-error').textContent = '';
  try {
    const result = await api('/api/transaction',payload); state = result.state; render(); $('#amount').value = ''; quote(); toast(result.message);
  } catch (error) { $('#form-error').textContent = error.message; }
  finally { busy = false; $('#submit-transaction').disabled = false; }
}

$('#deposit-tab').onclick = () => setMode('deposit'); $('#withdraw-tab').onclick = () => setMode('withdraw');
$('#amount').oninput = quote; $('#currency').onchange = quote;
$('#full-withdraw').onchange = () => { $('#amount').disabled = $('#full-withdraw').checked; $('#amount').required = !$('#full-withdraw').checked; quote(); };
$('#transaction-form').onsubmit = event => { event.preventDefault(); transact({kind:$('#full-withdraw').checked ? 'withdraw_all' : mode,currency:$('#currency').value,amount:$('#amount').value}); };
$('#sample-deposit').onclick = () => transact({kind:'deposit',currency:'GHS',amount:'100'});
document.querySelectorAll('nav a').forEach(link => link.onclick = () => { document.querySelectorAll('nav a').forEach(item => item.classList.toggle('active',item === link)); });
api('/api/state').then(result => { state = result; render(); }).catch(error => { $('#form-error').textContent = error.message; });
