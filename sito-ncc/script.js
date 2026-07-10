/* ==========================================================================
   Swiss NCC — script condiviso
   ========================================================================== */
(function () {
  'use strict';

  /* --- Menu mobile --- */
  var burger = document.getElementById('burger');
  var menu = document.getElementById('menu');
  if (burger && menu) {
    burger.addEventListener('click', function () {
      menu.classList.toggle('show');
      burger.classList.toggle('open');
    });
    menu.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () {
        menu.classList.remove('show');
        burger.classList.remove('open');
      });
    });
  }

  /* --- Reveal on scroll --- */
  var reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12 });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* --- FAQ accordion --- */
  document.querySelectorAll('.qa button').forEach(function (b) {
    b.addEventListener('click', function () {
      var qa = b.parentElement;
      var ans = qa.querySelector('.ans');
      var open = qa.classList.toggle('open');
      ans.style.maxHeight = open ? ans.scrollHeight + 'px' : 0;
    });
  });

  /* --- Quick book (home) --- */
  var qbForm = document.getElementById('qbform');
  if (qbForm) {
    var qbMode = 'transfer';
    document.querySelectorAll('.qb-seg button').forEach(function (b) {
      b.addEventListener('click', function () {
        document.querySelectorAll('.qb-seg button').forEach(function (x) { x.classList.remove('sel'); });
        b.classList.add('sel');
        qbMode = b.dataset.type;
        document.querySelectorAll('.qbook .only-transfer').forEach(function (e) {
          e.style.display = qbMode === 'transfer' ? '' : 'none';
        });
      });
    });
    var qd = document.getElementById('qb-date');
    if (qd) qd.min = new Date().toISOString().split('T')[0];
    qbForm.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var p = new URLSearchParams();
      p.set('mode', qbMode);
      var v = function (id) { var el = document.getElementById(id); return el ? el.value.trim() : ''; };
      if (v('qb-from')) p.set('from', v('qb-from'));
      if (qbMode === 'transfer' && v('qb-to')) p.set('to', v('qb-to'));
      if (v('qb-date')) p.set('date', v('qb-date'));
      if (v('qb-time')) p.set('time', v('qb-time'));
      location.href = 'prenota.html?' + p.toString();
    });
  }

  /* --- Wizard (prenota) --- */
  var wiz = document.getElementById('wiz-main');
  if (!wiz) return;

  var WA_NUM = '41767565725';
  var state = { mode: 'transfer', veh: '', pay: '' };
  var step = 1, TOTAL = 4;
  var steps = wiz.querySelectorAll('.wiz-step');
  var prevB = document.getElementById('wiz-prev');
  var nextB = document.getElementById('wiz-next');
  var subB = document.getElementById('wiz-submit');
  var bar = document.getElementById('wiz-bar');
  var lbl = document.getElementById('wiz-lbl');
  function q(id) { return document.getElementById(id); }

  /* mode toggle */
  document.querySelectorAll('.wiz-seg button').forEach(function (b) {
    b.addEventListener('click', function () {
      document.querySelectorAll('.wiz-seg button').forEach(function (x) { x.classList.remove('sel'); });
      b.classList.add('sel');
      state.mode = b.dataset.type;
      var tr = state.mode === 'transfer';
      document.querySelectorAll('.only-transfer').forEach(function (e) { e.style.display = tr ? '' : 'none'; });
      document.querySelectorAll('.only-ore').forEach(function (e) { e.style.display = tr ? 'none' : ''; });
      sync();
    });
  });

  /* vehicle select */
  document.querySelectorAll('.pick-card').forEach(function (c) {
    c.addEventListener('click', function () {
      document.querySelectorAll('.pick-card').forEach(function (x) { x.classList.remove('sel'); });
      c.classList.add('sel');
      state.veh = c.dataset.veh;
      sync();
    });
  });

  /* payment select */
  document.querySelectorAll('.pay-card').forEach(function (c) {
    c.addEventListener('click', function () {
      document.querySelectorAll('.pay-card').forEach(function (x) { x.classList.remove('sel'); });
      c.classList.add('sel');
      state.pay = c.dataset.pay;
    });
  });

  /* live sync */
  ['f-from', 'f-to', 'f-date', 'f-time', 'f-pax', 'f-hours'].forEach(function (id) {
    var el = q(id); if (el) el.addEventListener('input', sync);
  });
  var rt = q('f-rt'); if (rt) rt.addEventListener('change', sync);

  function sync() {
    q('s-type').textContent = state.mode === 'transfer'
      ? (q('f-rt').checked ? 'Transfer · A/R' : 'Transfer')
      : 'A ore (' + (q('f-hours').value || '—') + 'h)';
    var from = q('f-from').value.trim(), to = q('f-to').value.trim();
    q('s-route').textContent = state.mode === 'transfer'
      ? (from || '—') + (to ? ' → ' + to : '')
      : (from || '—');
    var d = q('f-date').value, t = q('f-time').value;
    q('s-when').textContent = d ? (d.split('-').reverse().join('/') + (t ? ' · ' + t : '')) : '—';
    q('s-pax').textContent = q('f-pax').value || '—';
    q('s-veh').textContent = state.veh || '—';
  }

  function show(n) {
    steps.forEach(function (s) { s.classList.toggle('act', +s.dataset.step === n); });
    bar.style.width = (n / TOTAL * 100) + '%';
    lbl.textContent = 'Passo ' + n + ' di ' + TOTAL;
    prevB.style.display = n > 1 ? '' : 'none';
    nextB.style.display = n < TOTAL ? '' : 'none';
    subB.style.display = n === TOTAL ? '' : 'none';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  nextB.addEventListener('click', function () {
    if (step === 1) {
      if (!q('f-from').value.trim()) { alert('Inserisci il luogo di partenza.'); return; }
      if (state.mode === 'transfer' && !q('f-to').value.trim()) { alert('Inserisci la destinazione.'); return; }
      if (!q('f-date').value || !q('f-time').value) { alert('Inserisci data e ora.'); return; }
    }
    if (step === 2 && !state.veh) { alert('Seleziona un veicolo.'); return; }
    if (step < TOTAL) { step++; show(step); }
  });
  prevB.addEventListener('click', function () { if (step > 1) { step--; show(step); } });

  function buildMsg() {
    var L = [];
    L.push('Ciao Swiss NCC, vorrei richiedere un preventivo.');
    L.push('');
    L.push('Tipo: ' + q('s-type').textContent);
    L.push('Tratta: ' + q('s-route').textContent);
    if (state.mode === 'ore') L.push('Durata: ' + (q('f-hours').value || '—') + ' ore');
    L.push('Data e ora: ' + q('s-when').textContent);
    L.push('Passeggeri: ' + (q('f-pax').value || '—'));
    L.push('Veicolo: ' + (state.veh || 'Da definire'));
    L.push('Pagamento: ' + (state.pay || 'Da concordare'));
    L.push('');
    L.push('Nome: ' + (q('f-name').value || '—'));
    L.push('Telefono: ' + (q('f-phone').value || '—'));
    L.push('Email: ' + (q('f-email').value || '—'));
    if (q('f-note').value.trim()) L.push('Note: ' + q('f-note').value.trim());
    return L.join('\n');
  }

  subB.addEventListener('click', function () {
    if (!state.pay) { alert('Seleziona una modalità di pagamento.'); return; }
    if (!q('f-name').value.trim() || !q('f-phone').value.trim()) {
      alert('Inserisci nome e telefono (passo 3).'); step = 3; show(3); return;
    }
    var waUrl = 'https://wa.me/' + WA_NUM + '?text=' + encodeURIComponent(buildMsg());
    document.getElementById('wiz-wrap').style.display = 'none';
    q('done').classList.add('show');
    window.scrollTo({ top: 0, behavior: 'smooth' });
    window.open(waUrl, '_blank');
  });

  /* default date = domani, min = oggi */
  (function () {
    var today = new Date().toISOString().split('T')[0];
    q('f-date').min = today;
  })();

  /* prefill da URL */
  (function () {
    var p = new URLSearchParams(location.search);
    if (p.get('mode') === 'ore') { var ob = document.querySelector('.wiz-seg button[data-type="ore"]'); if (ob) ob.click(); }
    if (p.get('from')) q('f-from').value = p.get('from');
    if (p.get('to')) q('f-to').value = p.get('to');
    if (p.get('date')) q('f-date').value = p.get('date');
    if (p.get('time')) q('f-time').value = p.get('time');
  })();

  sync();
  show(1);
})();
