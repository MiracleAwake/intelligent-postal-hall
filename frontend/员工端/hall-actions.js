/* 行内按键只此一套。状态决定给哪两颗，岗位页只负责把业务画进原来的名单。 */
(function () {
  var STATUS_ACT = {
    '待到店': [['remind', '提醒', true], ['detail', '详情', false]],
    '已到店': [['look', '查看', true], ['detail', '详情', false]],
    '已办结': [['review', '复看', false], ['detail', '详情', false]],
    '已过期': [['reappoint', '改约', false], ['detail', '详情', false]]
  };
  var STATUS_CLASS = {
    '待到店': 'st-wait',
    '已到店': 'st-here',
    '已办结': 'st-done',
    '已过期': 'st-late'
  };

  function roleOf() {
    var path = location.pathname;
    if (path.indexOf('06_') >= 0) return 'P1';
    if (path.indexOf('05_') >= 0) return 'P2';
    if (path.indexOf('07_') >= 0) return 'P3';
    if (path.indexOf('09_') >= 0) return 'P4';
    return '';
  }

  function esc(s) {
    return String(s == null ? '' : s)
      .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function buttons(status, reminded) {
    var acts = STATUS_ACT[status] || STATUS_ACT['待到店'];
    return acts.map(function (it) {
      var label = it[0] === 'remind' && reminded ? '已提醒' : it[1];
      var dis = it[0] === 'remind' && reminded ? ' disabled style="opacity:.6"' : '';
      return '<button type="button"' + (it[2] && !reminded ? ' class="pri"' : '') +
        ' data-act="' + it[0] + '"' + dis + '>' + label + '</button>';
    }).join('');
  }

  function rowHtml(item) {
    var st = STATUS_CLASS[item.status] || 'st-wait';
    return '<div class="lst-r" data-live="1" data-f="today" data-id="' + esc(item.id) + '">' +
      '<div class="cust"><span class="av">' + esc(item.name.charAt(0)) + '</span><span class="cn">' + esc(item.name) + '</span></div>' +
      '<div><span class="tag-line">' + esc(item.line) + '</span>' + esc(item.intent) + '</div>' +
      '<div>' + esc(item.slot) + '</div>' +
      '<div class="dim">' + esc(item.source) + '</div>' +
      '<div><span class="st ' + st + '">' + esc(item.status) + '</span></div>' +
      '<div class="op">' + buttons(item.status, item.reminded) + '</div>' +
      '</div>';
  }

  function note(row, text) {
    var old = row.querySelector('.live-note');
    if (old) old.parentNode.removeChild(old);
    var n = document.createElement('div');
    n.className = 'live-note';
    n.style.cssText = 'grid-column:1/-1;margin-top:4px;padding:6px 8px;border-radius:6px;background:#f4faf6;font-size:12px;color:#2b3a34';
    n.textContent = text;
    row.appendChild(n);
  }

  function explain(item, action) {
    if (action === 'look') {
      return item.actual
        ? '查看 · 到店后登记的待办：' + item.actual
        : '查看 · 人已经到店，大堂还没登记实际待办。';
    }
    if (action === 'detail' || action === 'review') {
      return '详情 · 预约时填的事项：' + item.intent + ' · ' + item.source;
    }
    if (action === 'reappoint') return '改约 · 这一笔回到待到店，时段等客户再定。';
    return '已提醒 · ' + item.name;
  }

  function paint(items) {
    var list = document.getElementById('apList');
    if (!list || !items.length) return;
    var html = items.map(rowHtml).join('');
    var head = list.querySelector('.lst-hd');
    if (head) head.insertAdjacentHTML('afterend', html);
    else list.insertAdjacentHTML('beforeend', html);
    var badge = document.querySelector('[data-sub="预约客户"] b');
    if (badge) badge.textContent = String((parseInt(badge.textContent, 10) || 0) + items.length);
  }

  function bind(role) {
    document.addEventListener('click', function (e) {
      var btn = e.target.closest && e.target.closest('[data-live="1"] button[data-act]');
      if (!btn) return;
      e.stopPropagation();
      var row = btn.closest('.lst-r');
      var id = row.getAttribute('data-id');
      var action = btn.getAttribute('data-act');
      fetch('/api/appointments/act', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: role, id: id, action: action })
      }).then(function (r) { return r.json(); }).then(function (res) {
        var item = res.item;
        if (!item) return;
        if (action === 'remind' || action === 'reappoint') {
          row.outerHTML = rowHtml(item);
          row = document.querySelector('[data-live="1"][data-id="' + id + '"]');
        }
        if (row) note(row, explain(item, action));
      }).catch(function () {});
    }, true);
  }

  var role = roleOf();
  if (!role || !document.getElementById('apList')) return;
  fetch('/api/appointments?role=' + encodeURIComponent(role))
    .then(function (r) { return r.json(); })
    .then(function (res) {
      paint(res.items || []);
      bind(role);
    })
    .catch(function () {});
})();
