/* 子页面上功能区以外的键。同一岗位每一页同一套去处。 */
(function () {
  if (!document.getElementById('hallAgentCss')) {
    var css = document.createElement('style');
    css.id = 'hallAgentCss';
    css.textContent = 'body.agent-min .main > .agent,body.agent-min aside.agent{flex:0 0 44px !important;width:44px !important;min-width:44px !important;max-width:44px !important;}body.agent-min #agent:not(.agent){flex:0 0 36px !important;width:36px !important;min-width:36px !important;max-width:36px !important;}';
    document.head.appendChild(css);
  }
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
  function hereFile() {
    var name = location.pathname.split('/').pop() || '';
    try { name = decodeURIComponent(name); } catch (e) {}
    return name.split('?')[0];
  }
  function labelOf(b) {
    return ((b && (b.innerText || b.getAttribute('title'))) || '').replace(/\s+/g, '');
  }
  function tip(msg) {
    var old = document.getElementById('hallKeyNote');
    if (old) old.parentNode.removeChild(old);
    var n = document.createElement('div');
    n.id = 'hallKeyNote';
    n.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#243028;color:#fff;border-radius:8px;padding:10px 14px;font-size:13px;z-index:90;max-width:420px';
    n.textContent = msg;
    document.body.appendChild(n);
    setTimeout(function () { if (n.parentNode) n.parentNode.removeChild(n); }, 2400);
  }
  function showPane(hash) {
    var btn = document.querySelector('#subNav button[data-sub="' + hash + '"]');
    if (btn) { btn.click(); return; }
    location.hash = hash;
  }
  function go(dest) {
    if (!dest) return;
    if (dest.indexOf('NOTE:') === 0) { tip(dest.slice(5)); return; }
    if (dest === '/') { location.href = '/挚邮员工端.html'; return; }
    var file = dest;
    var hash = '';
    var cut = dest.indexOf('#');
    if (cut >= 0) { file = dest.slice(0, cut); hash = dest.slice(cut + 1); }
    if (file === hereFile()) {
      if (hash) showPane(hash);
      else tip('就在这一页');
      return;
    }
    location.href = dest;
  }

  var WORD = {
    P2: [['工作台', '/'], ['业务', '05_业务.html'], ['账户', '05_账户.html'], ['客户', '05_客户.html'], ['活动', '05_活动.html'], ['统计', '05_统计.html'], ['联系人', '05_联系人.html']],
    P4: [['工作台', '/'], ['业务', '09_业务.html'], ['客户', '09_客户.html'], ['活动', '09_活动.html'], ['统计', '09_统计.html'], ['联系人', '09_联系人.html']]
  };
  var TAB = {
    P1: {
      '文件': '/',
      '会话': '06_业务.html',
      '审计留痕': '08_审计.html#操作留痕',
      '工具': 'NOTE:工具收在功能区，不另开一页',
      '观测': 'NOTE:观测限权，这一岗不打开',
      '观测限权': 'NOTE:观测限权，这一岗不打开',
      '帮助': 'NOTE:问模型写在右侧'
    },
    P3: {
      '文件': '/',
      '日终': 'NOTE:日终收在功能区：结算缴款、业务补录、验单处理、操作留痕',
      '工具': 'NOTE:工具收在功能区，不另开一页',
      '观测': 'NOTE:观测限权，这一岗不打开',
      '观测限权': 'NOTE:观测限权，这一岗不打开',
      '帮助': 'NOTE:问模型写在右侧'
    },
    P5: {
      '文件': '/',
      '人员网络': '08_组织.html#人员网络',
      '参数配置': '08_参数.html#业务参数',
      '数据管理': '08_数据.html#数据目录',
      '报表中心': '08_报表.html#全局报表',
      '审计合规': '08_审计.html#操作留痕',
      '接口与能力': '08_系统.html#接口与能力',
      '客户数据': 'NOTE:管理员不打开客户正文',
      '客户数据无查看权': 'NOTE:管理员不打开客户正文',
      '帮助': 'NOTE:管理端按岗位装配。客户数据无查看权。'
    }
  };

  function rebuildWordTabs() {
    var set = WORD[roleOf()];
    if (!set) return;
    var nav = document.querySelector('nav.rtabs');
    if (!nav) return;
    var word = false;
    var old = nav.querySelectorAll('.rt');
    for (var i = 0; i < old.length; i++) {
      if (labelOf(old[i]) === '开始') word = true;
    }
    if (!word) return;
    var here = hereFile();
    var html = '';
    for (var j = 0; j < set.length; j++) {
      var file = set[j][1].split('#')[0];
      html += '<button type="button" class="rt' + (file === here ? ' on' : '') + '" data-hk="' + set[j][1] + '">' + set[j][0] + '</button>';
    }
    var drop = [];
    for (var k = 0; k < nav.childNodes.length; k++) {
      var n = nav.childNodes[k];
      if (n.nodeType === 1 && (n.classList.contains('rt') || n.classList.contains('rt-sep'))) drop.push(n);
    }
    for (var d = 0; d < drop.length; d++) nav.removeChild(drop[d]);
    nav.insertAdjacentHTML('afterbegin', html);
  }
  function tagTabs() {
    var map = TAB[roleOf()];
    if (!map) return;
    var rts = document.querySelectorAll('nav.rtabs .rt');
    for (var i = 0; i < rts.length; i++) {
      if (rts[i].getAttribute('data-tabgo') || rts[i].getAttribute('data-hk')) continue;
      var dest = map[labelOf(rts[i])];
      if (dest) rts[i].setAttribute('data-hk', dest);
    }
  }
  function unstickRange() {
    if (!document.querySelector('.lst-r[data-f]')) return;
    var bs = document.querySelectorAll('#pgSeg button[data-f]');
    for (var i = 0; i < bs.length; i++) {
      bs[i].removeAttribute('data-p70off');
      bs[i].style.opacity = '';
      bs[i].style.cursor = '';
    }
  }

  rebuildWordTabs();
  tagTabs();
  unstickRange();

  function agentBox(b) {
    return (b.closest && (b.closest('#agent') || b.closest('.agent'))) || document;
  }
  function agentSend(b) {
    var box = agentBox(b);
    var ta = box.querySelector('textarea');
    if (!ta) { tip('这一页没有输入框'); return; }
    var v = (ta.value || '').replace(/^\s+|\s+$/g, '');
    if (!v) { tip('先写一句'); ta.focus(); return; }
    var body = box.querySelector('#agBody') || box.querySelector('.ag-body');
    if (body) {
      var line = document.createElement('div');
      line.style.cssText = 'margin:8px 12px;padding:8px 10px;background:#f4f7f5;border-radius:8px;font-size:13px;line-height:1.5';
      line.textContent = v;
      body.appendChild(line);
    }
    ta.value = '';
    tip('已记下');
  }
  function ask(title, done) {
    var reason = window.prompt(title);
    if (reason == null) return;
    reason = reason.replace(/^\s+|\s+$/g, '');
    if (!reason) { tip('先写原因'); return; }
    done(reason);
  }

  document.addEventListener('click', function (e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var col = t.closest('.ag-collapse') || t.closest('#btnAgentCollapse');
    if (col) {
      e.preventDefault();
      e.stopImmediatePropagation();
      var min = !document.body.classList.contains('agent-min');
      document.body.classList.toggle('agent-min', min);
      var top = document.getElementById('btnAgent');
      if (top) top.classList.toggle('on', !min);
      col.title = min ? '展开模型板块' : '收起模型板块';
      try {
        var flag = min ? '1' : '0';
        localStorage.setItem('w1.agent', flag);
        if (roleOf() === 'P5') {
          ['w9o.agent', 'w9a.agent', 'w9d.agent'].forEach(function (k) { localStorage.setItem(k, flag); });
        }
      } catch (err) {}
      return;
    }
    var rt = t.closest('nav.rtabs .rt');
    if (rt) {
      var dest = rt.getAttribute('data-hk');
      if (!dest) return;
      e.preventDefault();
      e.stopImmediatePropagation();
      go(dest);
      return;
    }
    var out = t.closest('button.out');
    if (out && out.id !== 'btnOut') {
      e.preventDefault();
      e.stopImmediatePropagation();
      if (!window.confirm('退出登录？会话留在本网点，不随人走。')) return;
      try { sessionStorage.removeItem('v10_session'); } catch (err) {}
      try { localStorage.removeItem('v10_session'); } catch (err2) {}
      location.href = '/挚邮员工端.html';
      return;
    }
    var bell = t.closest('button[title="通知"]');
    if (bell && bell.id !== 'btnBell') {
      e.preventDefault();
      e.stopImmediatePropagation();
      var role = roleOf();
      if (window.HallLive) { HallLive.openNotice(role); return; }
      fetch('/api/today?role=' + encodeURIComponent(role)).then(function (r) { return r.json(); }).then(function (d) {
        var notes = d.notices || [];
        var pins = d.pins || [];
        if (notes.length) tip('通知 · ' + notes[0].title);
        else if (pins.length) tip('通知 · ' + (pins[0].text || pins[0].title));
        else tip('现在没有新通知');
      }).catch(function () { tip('现在没有新通知'); });
      return;
    }
    if (t.closest('.tadd') || t.closest('.btn-new')) {
      e.preventDefault();
      e.stopImmediatePropagation();
      location.href = '/挚邮员工端.html';
      return;
    }
    var tx = t.closest('.tabs .tx');
    if (tx) {
      e.preventDefault();
      e.stopImmediatePropagation();
      var tab = tx.closest('.tab');
      if (!tab) return;
      if (tab.classList.contains('on')) { location.href = '/挚邮员工端.html'; return; }
      if (tab.parentNode) tab.parentNode.removeChild(tab);
      return;
    }
    var send = t.closest('#agent button.send, .agent button.send, button.ag-send');
    if (send) {
      e.preventDefault();
      e.stopImmediatePropagation();
      agentSend(send);
      return;
    }
    var ag = t.closest('#agent button, .agent button');
    if (ag) {
      var title = ag.getAttribute('title') || '';
      if (title === '新建对话') {
        e.preventDefault();
        e.stopImmediatePropagation();
        var ta = agentBox(ag).querySelector('textarea');
        if (ta) ta.value = '';
        tip('新的一句从这里开始');
        return;
      }
      if (title === '历史记录') {
        e.preventDefault();
        e.stopImmediatePropagation();
        tip('刚才记下的句子留在这一栏里');
        return;
      }
      if (title === '附件') {
        e.preventDefault();
        e.stopImmediatePropagation();
        var inp = document.getElementById('hallKeyFile');
        if (!inp) {
          inp = document.createElement('input');
          inp.id = 'hallKeyFile';
          inp.type = 'file';
          inp.hidden = true;
          inp.addEventListener('change', function () {
            var f = inp.files && inp.files[0];
            if (!f) return;
            var body = new FormData();
            body.append('file', f, f.name);
            fetch('/api/files', { method: 'POST', body: body }).then(function (r) { return r.json(); }).then(function (res) {
              tip('已附上 ' + (res.name || f.name));
            }).catch(function () { tip('附件没有送上去'); });
            inp.value = '';
          });
          document.body.appendChild(inp);
        }
        inp.click();
        return;
      }
    }
    var q = t.closest('button.qbtn');
    if (q && !q.id) {
      var qn = labelOf(q);
      if (qn === '标记误报（须填原因）') {
        e.preventDefault();
        e.stopImmediatePropagation();
        ask('误报原因', function (reason) {
          q.classList.add('on');
          tip('已标误报 · ' + reason);
        });
        return;
      }
      if (qn === '转合规核查') {
        e.preventDefault();
        e.stopImmediatePropagation();
        showPane('操作留痕');
        tip('已转入合规核查，留在操作留痕');
        return;
      }
      if (qn === '发起破玻璃（写理由）') {
        e.preventDefault();
        e.stopImmediatePropagation();
        ask('破玻璃理由', function (reason) {
          showPane('破玻璃记录');
          tip('已记下破玻璃 · ' + reason);
        });
        return;
      }
      if (qn === '审批待办（合规岗）') {
        e.preventDefault();
        e.stopImmediatePropagation();
        showPane('破玻璃记录');
        tip('合规岗待办在破玻璃记录这一格');
        return;
      }
    }
    var add = t.closest('button.add');
    if (add) {
      e.preventDefault();
      e.stopImmediatePropagation();
      tip('新任务从「新建会话」进');
    }
  }, true);

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('#pgSeg button[data-f]');
    if (!b || b.getAttribute('data-p70off')) return;
    var f = b.getAttribute('data-f');
    var sibs = b.parentNode.querySelectorAll('button');
    for (var i = 0; i < sibs.length; i++) sibs[i].classList.toggle('on', sibs[i] === b);
    if (f === 'on' || f === 'all') {
      var chip = document.querySelector('#ctChips [data-cf="' + (f === 'on' ? 'on' : 'all') + '"]');
      if (chip) { chip.click(); return; }
    }
    var rows = document.querySelectorAll('.lst-r[data-f]');
    if (!rows.length) return;
    for (var r = 0; r < rows.length; r++) {
      var rf = rows[r].getAttribute('data-f');
      var show = f === 'all' || rf === f || (f === 'week' && (rf === 'today' || rf === 'week'));
      rows[r].hidden = !show;
    }
  });
})();
