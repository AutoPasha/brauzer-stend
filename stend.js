// Журнал стенда: что пользователь на самом деле сделал. Хранится в localStorage
// этого браузера и выводится в каждую страницу блоком <script id="stend-journal">,
// чтобы итог читался из HTML страницы, а не на глаз.
(function () {
  var KEY = 'brauzer-stend';

  function journal() {
    try { return JSON.parse(localStorage.getItem(KEY) || '[]'); } catch (e) { return []; }
  }

  function render() {
    var el = document.getElementById('stend-journal');
    if (!el) {
      el = document.createElement('script');
      el.type = 'application/json';
      el.id = 'stend-journal';
      document.body.appendChild(el);
    }
    el.textContent = JSON.stringify(journal());
  }

  function log(ev, data) {
    var j = journal();
    var row = { ev: ev, page: location.pathname.split('/').pop() || 'index.html' };
    for (var k in (data || {})) row[k] = data[k];
    j.push(row);
    localStorage.setItem(KEY, JSON.stringify(j));
    render();
  }

  function store(name, value) {
    if (value === undefined) {
      try { return JSON.parse(localStorage.getItem(KEY + ':' + name) || 'null'); } catch (e) { return null; }
    }
    localStorage.setItem(KEY + ':' + name, JSON.stringify(value));
  }

  async function sha256(text) {
    var buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
  }

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function show(el, on) { el.hidden = !on; }

  function param(name) { return new URLSearchParams(location.search).get(name); }

  window.Stend = { log: log, journal: journal, store: store, sha256: sha256, $: $, $$: $$, show: show, param: param };
  document.addEventListener('DOMContentLoaded', render);
})();
