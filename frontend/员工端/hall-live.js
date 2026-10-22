/* 今日必办、任务栏、通知中心只走这一份。
   图标按事务类型取，确认和去处理落到能办这件事的页面。 */
window.HallLive = (function () {
  var KINDS = [
    [/调岗/, 'g-transfer', '调岗', 'lead'],
    [/密钥/, 'g-key', '密钥', 'lead'],
    [/权限|授权/, 'g-shield', '权限', 'lead'],
    [/备份/, 'g-file', '备份', 'sys'],
    [/归档|数据/, 'g-db', '数据', 'sys'],
    [/参数/, 'g-gear', '参数', 'sys'],
    [/维护/, 'g-gear', '维护', 'sys'],
    [/回访/, 'g-phone', '回访', 'visit'],
    [/预约/, 'g-cal', '预约', 'appt'],
    [/例会/, 'g-users', '例会', 'lead'],
    [/验视/, 'g-eye', '验视', 'visit'],
    [/日终|结算/, 'g-coins', '日终', 'sys'],
    [/代办/, 'g-doc', '代办', 'sys'],
    [/收寄|取件/, 'g-box', '收寄', 'appt'],
    [/邮务|订阅|报刊/, 'g-doc', '邮务', 'appt'],
    [/巡检/, 'g-eye', '巡检', 'sys'],
    [/转交/, 'g-transfer', '转交', 'lead']
  ];
  var PATHS = {
    'g-transfer': '<circle cx="9" cy="7.6" r="3.2"/><path d="M3 19.6c0-3.3 2.7-6 6-6M15.6 9.4h5.6M18.8 6.2l3.2 3.2-3.2 3.2"/>',
    'g-key': '<circle cx="8" cy="12" r="3.4"/><path d="M11.4 12h9.2M17.4 12v3.4M20.6 12v2.4"/>',
    'g-shield': '<path d="M12 3l7.6 3v6.1c0 4.4-3.1 7.9-7.6 9-4.5-1.1-7.6-4.6-7.6-9V6z"/><path d="M9 12.1l2.2 2.2 4.3-4.5"/>',
    'g-file': '<path d="M6 3h7.4l4.6 4.6V21H6z"/><path d="M13.4 3v4.6H18"/>',
    'g-db': '<ellipse cx="12" cy="6" rx="7.4" ry="3.2"/><path d="M4.6 6v12c0 1.8 3.3 3.2 7.4 3.2s7.4-1.4 7.4-3.2V6"/><path d="M4.6 12c0 1.8 3.3 3.2 7.4 3.2s7.4-1.4 7.4-3.2"/>',
    'g-gear': '<circle cx="12" cy="12" r="3.2"/><path d="M12 3.2v2.4M12 18.4v2.4M4.6 12H2.2M21.8 12h-2.4M6.7 6.7L5 5M19 19l-1.7-1.7M6.7 17.3L5 19M19 5l-1.7 1.7"/>',
    'g-phone': '<path d="M8 3.6h8a1.6 1.6 0 011.6 1.6v13.6a1.6 1.6 0 01-1.6 1.6H8a1.6 1.6 0 01-1.6-1.6V5.2A1.6 1.6 0 018 3.6z"/><path d="M11 18.2h2"/>',
    'g-cal': '<rect x="3.6" y="5" width="16.8" height="16" rx="2"/><path d="M8 3v4M16 3v4M3.6 10.4h16.8"/>',
    'g-users': '<circle cx="9" cy="8.4" r="3.2"/><path d="M3.6 19.4c0-3 2.4-5.4 5.4-5.4s5.4 2.4 5.4 5.4"/><path d="M16.2 6.2a3.2 3.2 0 010 6.2M17.4 19.4c0-2.2-.7-4.2-2-5.6"/>',
    'g-eye': '<path d="M2.6 12S6.2 5.6 12 5.6 21.4 12 21.4 12 17.8 18.4 12 18.4 2.6 12 2.6 12z"/><circle cx="12" cy="12" r="3.1"/>',
    'g-coins': '<ellipse cx="12" cy="7" rx="7" ry="3"/><path d="M5 7v5c0 1.7 3.1 3 7 3s7-1.3 7-3V7"/><path d="M5 12v5c0 1.7 3.1 3 7 3s7-1.3 7-3v-5"/>',
    'g-doc': '<path d="M6 3h7.4l4.6 4.6V21H6z"/><path d="M13.4 3v4.6H18"/><path d="M9 12.6h6M9 16h4"/>',
    'g-box': '<path d="M3.4 7.6L12 3.2l8.6 4.4v8.8L12 20.8 3.4 16.4z"/><path d="M3.4 7.6L12 12l8.6-4.4M12 12v8.8"/>',
    'g-bell': '<path d="M18 8.6a6 6 0 10-12 0c0 5-2 6.4-2 6.4h16s-2-1.4-2-6.4z"/><path d="M13.7 19a2 2 0 01-3.4 0"/>'
  };
  var PAGE = {
    P5: {
      数据: '08_数据.html#数据目录',
      维护: '08_系统.html#服务状态',
      系统: '08_系统.html#服务状态',
      参数: '08_参数.html#业务参数',
      调岗: '08_组织.html#调岗与交接',
      权限: '08_组织.html#权限授予',
      密钥: '08_数据.html#生命周期',
      备份: '08_数据.html#备份与归档',
      审计: '08_审计.html#操作留痕'
    },
    P1: {
      回访: '06_客户.html#待回访',
      预约: '06_客户.html#预约客户',
      客户: '06_客户.html#重点客户',
      权限: '06_授权.html#待我授权',
      授权: '06_授权.html#待我授权',
      人员: '06_员工.html#本局'
    },
    P2: {
      回访: '05_客户.html#待回访',
      预约: '05_客户.html#预约客户',
      客户: '05_客户.html#重点客户'
    },
    P3: {
      回访: '07_客户.html#待回访',
      预约: '07_客户.html#预约客户',
      客户: '07_客户.html#重点客户',
      代办: '07_代办.html#社保',
      验视: '07_收寄.html#在办收寄',
      收寄: '07_收寄.html#在办收寄',
      邮务: '07_邮务.html#报刊订阅',
      日终: '07_统计.html#我的收寄量'
    },
    P4: {
      回访: '09_客户.html#待回访',
      预约: '09_业务.html#预约管理',
      客户: '09_客户.html#重点客户',
      巡检: '09_业务.html#厅堂巡检'
    }
  };
  var TINT = {
    lead: ['#f0eaff', '#6b4fbb'],
    sys: ['#f1f2f4', '#5b6270'],
    visit: ['#fdeee0', '#b35309'],
    appt: ['#eef4ff', '#2b6cb0']
  };
  var feed = null;
  var pinAt = 0;

  function roleOf() {
    var path = '';
    try { path = decodeURIComponent(location.pathname); } catch (e) { path = location.pathname; }
    if (path.indexOf('06_') >= 0) return 'P1';
    if (path.indexOf('05_') >= 0) return 'P2';
    if (path.indexOf('07_') >= 0) return 'P3';
    if (path.indexOf('09_') >= 0) return 'P4';
    if (path.indexOf('08_') >= 0) return 'P5';
    return '';
  }
  function onSub() {
    var path = '';
    try { path = decodeURIComponent(location.pathname); } catch (e) { path = location.pathname; }
    return path.indexOf('二级页') >= 0 || /0[5-9]_/.test(path);
  }
  function hereFile() {
    var name = location.pathname.split('/').pop() || '';
    try { name = decodeURIComponent(name); } catch (e) {}
    return name.split('?')[0];
  }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function kind(title, source, group) {
    var blob = (title || '') + ' ' + (group || '') + ' ' + (source || '');
    for (var i = 0; i < KINDS.length; i++) {
      if (KINDS[i][0].test(blob)) return { i: KINDS[i][1], sn: KINDS[i][2], tone: KINDS[i][3] };
    }
    return { i: 'g-bell', sn: source || group || '事务', tone: 'sys' };
  }
  function destOf(role, item) {
    if (!item) return '';
    var k = kind(item.title || item.t || item.text, item.source, item.group);
    var table = PAGE[role] || {};
    return table[k.sn] || table[item.group] || '';
  }
  function ensureSprite() {
    if (document.getElementById('hallIconSprite')) return;
    var parts = [];
    Object.keys(PATHS).forEach(function (id) {
      parts.push('<symbol id="hall-' + id + '" viewBox="0 0 24 24">' + PATHS[id] + '</symbol>');
    });
    var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('id', 'hallIconSprite');
    svg.setAttribute('aria-hidden', 'true');
    svg.style.cssText = 'position:absolute;width:0;height:0;overflow:hidden';
    svg.innerHTML = parts.join('');
    document.body.appendChild(svg);
  }
  function icon(id, cls) {
    ensureSprite();
    return '<svg class="' + cls + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><use href="#hall-' + id + '"/></svg>';
  }
  function ensureCss() {
    if (document.getElementById('hallLiveCss')) return;
    var s = document.createElement('style');
    s.id = 'hallLiveCss';
    s.textContent = [
      '#hallNtc{position:fixed;inset:0;z-index:90}',
      '#hallNtc .mask{position:absolute;inset:0;background:rgba(20,24,22,.28)}',
      '#hallNtc .box{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:min(700px,94vw);background:#fff;border-radius:14px;box-shadow:0 18px 50px rgba(20,24,22,.18);display:flex;flex-direction:column;max-height:86vh}',
      '#hallNtc .hd{display:flex;align-items:center;gap:9px;padding:13px 16px;border-bottom:1px solid #eef0f3}',
      '#hallNtc .hd .ic{width:28px;height:28px;border-radius:8px;background:#e7f5ee;color:#00693e;display:grid;place-items:center;flex:none}',
      '#hallNtc .hd .ic svg{width:16px;height:16px}',
      '#hallNtc .hd b{display:block;font-size:15px}',
      '#hallNtc .hd span{display:block;margin-top:2px;color:#8b918a;font-size:12px}',
      '#hallNtc .x{margin-left:auto;border:0;background:transparent;font-size:18px;color:#667;cursor:pointer}',
      '#hallNtc .bd{overflow:auto}',
      '#hallNtc .row{display:flex;gap:9px;align-items:center;padding:14px 16px;border-bottom:1px solid #eef0f3}',
      '#hallNtc .row:last-child{border-bottom:0}',
      '#hallNtc .nic{width:28px;height:28px;border-radius:8px;display:grid;place-items:center;flex:none}',
      '#hallNtc .nic svg{width:16px;height:16px}',
      '#hallNtc .nb{flex:1;min-width:0}',
      '#hallNtc .nb b{display:block;font-size:13.5px}',
      '#hallNtc .nb .sub{margin-top:3px;color:#8b918a;font-size:12px}',
      '#hallNtc .go{flex:none;border:1px solid #d9d3ea;background:#f7f4ff;color:#6b4fbb;border-radius:8px;padding:4px 12px;cursor:pointer}',
      '#hallNtc .ft{display:flex;justify-content:flex-end;padding:10px 16px 14px}',
      '#hallNtc .ft button{border:1px solid #e1e4e2;background:#fff;border-radius:8px;padding:6px 14px;cursor:pointer}',
      '#hallNtc .empty{padding:16px;color:#8b918a;font-size:13px}'
    ].join('');
    document.head.appendChild(s);
  }
  function openDest(dest, refresh) {
    if (!dest) return;
    if (!onSub() && dest.indexOf('08_') === 0 && window.HallShell && HallShell.open) {
      HallShell.open(dest);
      if (refresh && HallShell.refresh) HallShell.refresh();
      return;
    }
    var file = dest.split('#')[0];
    var hash = dest.split('#')[1] || '';
    var url = onSub() ? dest : ('二级页/' + dest);
    if (file === hereFile()) {
      var btn = document.querySelector('#subNav button[data-sub="' + hash + '"]');
      if (btn) btn.click();
      else if (hash) location.hash = hash;
      if (refresh) boot();
      return;
    }
    location.href = url;
  }
  function confirmAndGo(role, id, item, after) {
    var dest = destOf(role, item);
    function go() {
      closeNotice();
      if (after) after(dest);
      else openDest(dest, true);
    }
    if (!id) { go(); return; }
    fetch('/api/today/confirm', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: role, id: Number(id) })
    }).then(go).catch(go);
  }
  function closeNotice() {
    var n = document.getElementById('hallNtc');
    if (n && n.parentNode) n.parentNode.removeChild(n);
  }
  function noticeHtml(list) {
    return (list || []).map(function (n) {
      var k = kind(n.title, n.group, n.body);
      var tint = TINT[k.tone] || TINT.sys;
      if (!n.duty_id) {
        return '<div class="row"><span class="nic" style="background:' + tint[0] + ';color:' + tint[1] + '">' +
          icon(k.i, '') + '</span><div class="nb"><b>' + esc(n.title) + '</b><div class="sub">' + esc(n.body) +
          '</div></div><span class="go">转交</span></div>';
      }
      return '<div class="row"><span class="nic" style="background:' + tint[0] + ';color:' + tint[1] + '">' +
        icon(k.i, '') + '</span><div class="nb"><b>' + esc(n.title) + '</b><div class="sub">' + esc(n.body) +
        '</div></div><button type="button" class="go" data-duty="' + esc(n.duty_id) + '" data-title="' +
        esc(n.title) + '" data-group="' + esc(n.group || '') + '">确认</button></div>';
    }).join('') || '<div class="empty">今天没有需要处理的通知。</div>';
  }
  function openNotice(role, cached) {
    ensureCss();
    function draw(data) {
      closeNotice();
      var wrap = document.createElement('div');
      wrap.id = 'hallNtc';
      wrap.innerHTML = '<div class="mask" data-x="1"></div><div class="box" role="dialog" aria-label="通知中心">' +
        '<div class="hd"><span class="ic">' + icon('g-bell', '') + '</span><div><b>通知中心</b><span>必办到了今天会进来，转交也在这里</span></div>' +
        '<button type="button" class="x" data-x="1" aria-label="关闭">✕</button></div>' +
        '<div class="bd">' + noticeHtml((data && data.notices) || []) + '</div>' +
        '<div class="ft"><button type="button" data-x="1">关闭</button></div></div>';
      document.body.appendChild(wrap);
      wrap.addEventListener('click', function (e) {
        var b = e.target.closest && e.target.closest('[data-duty]');
        if (b) {
          e.preventDefault();
          confirmAndGo(role, b.getAttribute('data-duty'), {
            title: b.getAttribute('data-title'),
            group: b.getAttribute('data-group')
          });
          return;
        }
        if (e.target.closest && e.target.closest('[data-x]')) closeNotice();
      });
    }
    if (cached && cached.ready) { draw(cached); return; }
    fetch('/api/today?role=' + encodeURIComponent(role)).then(function (r) { return r.json(); }).then(draw).catch(function () { draw({ notices: [] }); });
  }
  function taskRow(item, today) {
    var k = kind(item.title, item.source, item.group);
    var tint = TINT[k.tone] || TINT.sys;
    var dest = destOf(roleOf(), item);
    return '<div class="task" data-go="' + esc(dest) + '" title="' + esc(item.text || item.title) + '">' +
      icon(k.i, 'tk-i') +
      '<div class="tk-b"><div class="tk-t">' + esc(item.title) + '</div>' +
      '<div class="tk-s"><span class="src" style="background:' + tint[0] + ';color:' + tint[1] + '">' + esc(k.sn) + '</span>' +
      (item.detail ? '<span>' + esc(item.detail) + '</span>' : '') +
      '<span class="tk-tm' + (today ? ' today' : '') + '">' + (today ? '今日' : '未到期') + '</span></div></div>' +
      '<span class="dot" title="未处理"></span></div>';
  }
  function paintTasks(data, role) {
    var pins = data.pins || [];
    var later = data.later || [];
    var todayBox = document.getElementById('tkToday');
    var futureBox = document.getElementById('tkFuture');
    if (todayBox) {
      todayBox.innerHTML = pins.map(function (x) { return taskRow(x, true); }).join('') ||
        '<div class="task"><div class="tk-b"><div class="tk-t">今天没有到期事务</div></div></div>';
      if (futureBox) futureBox.innerHTML = later.map(function (x) { return taskRow(x, false); }).join('');
      var more = document.getElementById('tkMore');
      if (more) more.hidden = true;
      bindGo(todayBox);
      if (futureBox) bindGo(futureBox);
      return;
    }
    var scroll = document.querySelector('.sb-scroll');
    if (!scroll) return;
    var old = scroll.querySelector('[data-hall-tasks]');
    if (!old) {
      old = document.createElement('div');
      old.setAttribute('data-hall-tasks', '1');
      var anchor = scroll.querySelector('.sb-pinned') || null;
      var head = null;
      Array.prototype.forEach.call(scroll.children, function (el) {
        if (el.classList && el.classList.contains('sb-h') && /任务/.test(el.textContent || '')) head = el;
      });
      if (head && head.nextSibling) scroll.insertBefore(old, head.nextSibling);
      else if (anchor) scroll.insertBefore(old, anchor);
      else scroll.appendChild(old);
      Array.prototype.forEach.call(scroll.querySelectorAll(':scope > .pin-sec, :scope > .task, :scope > .more'), function (el) {
        if (!old.contains(el)) el.parentNode.removeChild(el);
      });
    }
    var html = '';
    if (pins.length) html += '<div class="pin-sec">今日到期</div>' + pins.map(function (x) { return taskRow(x, true); }).join('');
    if (later.length) html += '<div class="pin-sec">未来到期</div>' + later.map(function (x) { return taskRow(x, false); }).join('');
    if (!html) html = '<div class="pin-sec">今日到期</div><div class="task"><div class="tk-b"><div class="tk-t">今天没有到期事务</div></div></div>';
    old.innerHTML = html;
    bindGo(old);
  }
  function bindGo(host) {
    if (!host || host.getAttribute('data-go-bound')) return;
    host.setAttribute('data-go-bound', '1');
    host.addEventListener('click', function (e) {
      var row = e.target.closest && e.target.closest('[data-go]');
      if (!row) return;
      var dest = row.getAttribute('data-go');
      if (dest) openDest(dest);
    });
  }
  function paintPin(data, role) {
    var card = document.querySelector('.todocard');
    if (!card) return;
    var pins = data.pins || [];
    if (!pins.length) { card.hidden = true; return; }
    card.hidden = false;
    if (pinAt >= pins.length) pinAt = 0;
    var item = pins[pinAt];
    var due = data.due || pins.length;
    var num = card.querySelector('#tcNum');
    var text = card.querySelector('#tcText');
    var page = card.querySelector('#tcPage');
    if (num) num.textContent = pins.length + '/' + due;
    if (text) text.textContent = item.text || item.title || '';
    if (page) page.textContent = (pinAt + 1) + '/' + pins.length;
    var ring = card.querySelector('#tcRing') || card.querySelector('circle[stroke-dasharray]');
    if (ring) {
      var circ = 56.5;
      var fill = due ? ((due - pins.length) / due) * circ : 0;
      ring.setAttribute('stroke-dasharray', fill.toFixed(1) + ' ' + circ);
    }
    var go = card.querySelector('.go');
    if (go && go.tagName !== 'BUTTON') {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'go';
      b.textContent = '去处理';
      go.parentNode.replaceChild(b, go);
      go = b;
    }
    if (go) {
      go.onclick = function (e) {
        e.preventDefault();
        e.stopPropagation();
        confirmAndGo(role, item.id, item);
      };
    }
    var prev = card.querySelector('#tcPrev');
    var next = card.querySelector('#tcNext');
    if (prev) prev.onclick = function () { pinAt = (pinAt - 1 + pins.length) % pins.length; paintPin(data, role); };
    if (next) next.onclick = function () { pinAt = (pinAt + 1) % pins.length; paintPin(data, role); };
  }
  function wireStaticGo(role) {
    var card = document.querySelector('.todocard');
    if (!card) return;
    var go = card.querySelector('.go');
    if (!go || go.tagName === 'BUTTON') return;
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'go';
    b.textContent = '去处理';
    go.parentNode.replaceChild(b, go);
    b.onclick = function (e) {
      e.preventDefault();
      var text = (card.querySelector('#tcText') || {}).textContent || '';
      var dest = destOf(role, { title: text });
      if (dest) openDest(dest);
    };
  }
  function boot() {
    if (!onSub()) return;
    var role = roleOf();
    if (!role) return;
    fetch('/api/today?role=' + encodeURIComponent(role)).then(function (r) { return r.json(); }).then(function (data) {
      feed = data || {};
      if (!feed.applies) { wireStaticGo(role); return; }
      paintTasks(feed, role);
      paintPin(feed, role);
    }).catch(function () { wireStaticGo(role); });
  }
  if (document.body) boot();
  else document.addEventListener('DOMContentLoaded', boot);

  return {
    kind: kind,
    icon: icon,
    destOf: destOf,
    confirmAndGo: confirmAndGo,
    openNotice: openNotice,
    noticeHtml: noticeHtml
  };
})();
