// static/js/agents_whatsapp_rotate.js
(function () {
  function parseNumbers(raw) {
    if (!raw) return [];
    return raw.split(',').map(function (s) {
      return s.replace(/[^0-9]/g, '').trim();
    }).filter(Boolean).slice(0,3); // take up to 3 numbers
  }

  function openWA(number) {
    if (!number) return null;
    var url = "https://wa.me/" + number;
    window.open(url, '_blank');
  }

  document.querySelectorAll('tr.agent-row').forEach(function (row) {
    var raw = row.getAttribute('data-whatsapp') || '';
    var list = parseNumbers(raw);
    row._widx = 0;
    row._wa_list = list;

    row.querySelectorAll('.cell-link').forEach(function (link) {
      link.addEventListener('click', function (ev) {
        ev.preventDefault();
        var waList = row._wa_list;
        if (!waList || waList.length === 0) {
          if (window.VELKI_GLOBAL_WHATSAPP) {
            openWA(window.VELKI_GLOBAL_WHATSAPP);
            return;
          }
          alert('No WhatsApp number configured for this agent.');
          return;
        }
        var idx = row._widx || 0;
        idx = idx % waList.length;
        var number = waList[idx];
        openWA(number);
        row._widx = (idx + 1) % waList.length;
      });
    });
  });
})();


