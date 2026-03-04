/* logs-filter.js — filter buttons for Research Logs index */
(function () {
  var items   = Array.from(document.querySelectorAll('.logs-artifact-item'));
  var buttons = Array.from(document.querySelectorAll('.filter-btn'));
  var noRes   = document.getElementById('no-results');
  if (!buttons.length) return;

  // Count per tag
  var counts = { all: items.length, ifid: 0, a11y: 0, tool: 0, ai: 0 };
  items.forEach(function (item) {
    var tags = (item.getAttribute('data-tags') || '').split(' ');
    tags.forEach(function (t) { if (counts[t] !== undefined) counts[t]++; });
  });
  Object.keys(counts).forEach(function (k) {
    var el = document.getElementById('count-' + k);
    if (el) el.textContent = counts[k];
  });

  function applyFilter(filter) {
    var visible = 0;
    items.forEach(function (item) {
      var tags = (item.getAttribute('data-tags') || '').split(' ');
      var show = filter === 'all' || tags.indexOf(filter) !== -1;
      item.setAttribute('data-hidden', show ? 'false' : 'true');
      if (show) visible++;
    });
    if (noRes) noRes.classList.toggle('visible', visible === 0);
    document.querySelectorAll('.year-group').forEach(function (section) {
      var visibleInSection = Array.from(section.querySelectorAll('.logs-artifact-item'))
        .some(function (i) { return i.getAttribute('data-hidden') !== 'true'; });
      section.style.display = visibleInSection ? '' : 'none';
    });
  }

  buttons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      buttons.forEach(function (b) {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
      applyFilter(btn.getAttribute('data-filter'));
    });
  });

  applyFilter('all');
}());
