/* 第 1 格 · 12 个专属视图。渲染从母件搬来，数据入口按岗位分。
   母件行号见各函数上一行注释。 */
(function () {
  var ROLE = 'P1';
  var ME = { no: '1001', name: '王××' };
  var SESSION_NO = '1001';
  var SCOPE = 'net';
  var MODE = 'finance';
  function isoDay(d) {
    var m = d.getMonth() + 1, day = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
  }
  function shiftDay(iso, delta) {
    var p = iso.split('-');
    var d = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    d.setDate(d.getDate() + delta);
    return isoDay(d);
  }
  var DAY = isoDay(new Date());
  var ROLE_FROM_API = { P3: 'P1', P1: 'P2', P2: 'P3', P4: 'P4', P5: 'P5' };
  function toShellRole(code) { return ROLE_FROM_API[code] || ''; }
  var STAFF = [
    { no: '1001', name: '王××', role: 'P1', st: '在岗', gap: '' },
    { no: '1003', name: '赵××', role: 'P2', st: '在岗', gap: '' },
    { no: '1017', name: '秦××', role: 'P3', st: '在岗', gap: '' },
    { no: '1004', name: '孙××', role: 'P4', st: '在岗', gap: '' },
    { no: '9001', name: '区管理员', role: 'P5', st: '在岗', gap: '' },
    { no: '1002', name: '钱××', role: '', st: '在岗', gap: '后端无角色' },
    { no: '1010', name: '褚××', role: '', st: '在岗', gap: '后端无角色' },
    { no: '1018', name: '尤××', role: '', st: '在岗', gap: '后端无角色' },
    { no: '1022', name: '施××', role: '', st: '拒绝', gap: '后端无角色' }
  ];
  var OFF = [];
  function voterRow(s) {
    return s.st === '在岗' && s.no !== '1022' && s.no !== '9001' && s.no !== '1010' && s.no !== '1018';
  }
  var VOTERS = STAFF.filter(voterRow).map(function (s) { return s.no; });
  var CH_CLS = { '存量维护': 'stock', '走访新拓': 'new', '电联唤醒': 'call', '厅堂转介': 'rec' };
  var ST = {
    ok: ['已完成 · 全票通过', 's-ok'], wait: ['待确认', 's-wait'],
    draft: ['模型录入 · 待本人核对', 's-draft'], rej: ['已驳回', 's-rej']
  };
  var BASE = [
    { t: '15:44', k: '理财', a: 12.0, u: 'money', src: '手工', byNo: '1002', vn: 11 },
    { t: '15:18', k: '活期', a: 8.0, u: 'money', src: '手工', byNo: '1003', vn: 19 },
    { t: '14:52', k: '活期', a: 10.0, u: 'money', src: '模型', byNo: '1004', vn: 0, draft: 1, cl: '崔××（尾号 0417）', ch: '走访新拓' },
    { t: '14:05', k: '活期', a: 12.5, u: 'money', src: '模型', byNo: '1004', vn: 0, draft: 1, cl: '邵××（尾号 1123）', ch: '存量维护' },
    { t: '13:40', k: '定期', a: 10.0, u: 'money', src: '手工', byNo: '1002', vn: 11 },
    { t: '11:12', k: '定期', a: 20.0, u: 'money', src: '手工', byNo: '1002', vn: 6 },
    { t: '10:06', k: '定期', a: 26.0, u: 'money', src: '手工', byNo: '1003', vn: 19 },
    { t: '09:24', k: '定期', a: 30.0, u: 'money', src: '手工', byNo: '1003', vn: 19 }
  ];
  var PERF = [];
  var DEAD = [];
  var HALL = { windows: [], kiosks: [], queue: [], appts: [], tablet: { acts: [], note: '' } };
  var DRILL = {};

  var ICON = 'g-trace';
  function icon(id, cls) {
    return '<svg class="' + (cls || 'ic') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><use href="#' + id + '"/></svg>';
  }
  function $(id) { return document.getElementById(id); }
  function f1(n) { return Number(n).toFixed(1); }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
  function GUARD_N() { return STAFF.filter(function (s) { return s.role === 'P7'; }).length; }
  function meNo() { return ME && ME.no || ''; }
  function byOf(r) { return r.byNo || ''; }
  function nameOf(no) {
    var s = STAFF.filter(function (x) { return x.no === no; })[0];
    return s ? s.name : (no || '');
  }
  function isMine() { return SCOPE === 'mine'; }
  function scopeRows() { return isMine() ? PERF.filter(function (r) { return byOf(r) === meNo(); }) : PERF; }
  function needOf(r) { return VOTERS.filter(function (n) { return n !== byOf(r); }).length; }
  function votesOf(r) { return r.v || (r.v = []); }
  function rejsOf(r) { return r.rj || (r.rj = []); }
  function stOf(r) {
    if (r.draft) return 'draft';
    if (rejsOf(r).length) return 'rej';
    return votesOf(r).length >= needOf(r) ? 'ok' : 'wait';
  }
  function pendingOf(r) {
    var v = votesOf(r);
    var ab = (r.absent || []).map(function (x) { return x.no; });
    return VOTERS.filter(function (n) { return n !== byOf(r) && v.indexOf(n) < 0 && ab.indexOf(n) < 0; });
  }
  function canVote(r) {
    return VOTERS.indexOf(meNo()) >= 0 && byOf(r) !== meNo() && !r.draft && stOf(r) === 'wait' && votesOf(r).indexOf(meNo()) < 0;
  }
  function counts(list) {
    var c = { ok: 0, wait: 0, draft: 0, rej: 0 };
    (list || PERF).forEach(function (r) { c[stOf(r)]++; });
    return c;
  }
  function sumOf(list) { var s = 0; list.forEach(function (r) { s += Number(r.a) || 0; }); return s; }
  function chTag(ch) {
    if (!ch) return '<span class="dim">—</span>';
    return '<span class="pf-ch ' + (CH_CLS[ch] || 'stock') + '">' + ch + '</span>';
  }
  function box(t, v, u, cls, sub) {
    return '<div class="box"><div class="t">' + t + '</div><div class="v ' + (cls || '') + '">' +
      v + (u ? '<u>' + u + '</u>' : '') + '</div>' + (sub ? '<div class="s">' + sub + '</div>' : '') + '</div>';
  }
  function vbar(got, need, draft) {
    if (draft) return '<span class="pf-vt">未开始计票</span>';
    var pct = need ? Math.round(got / need * 100) : 0;
    var cls = got >= need ? '' : 'warn';
    return '<span class="pf-vbar"><i class="' + cls + '" style="width:' + pct + '%"></i></span>' +
      '<span class="pf-vt' + (got >= need ? '' : ' bad') + '"><b>' + got + '</b>/' + need + '</span>';
  }
  function deadDays(d) {
    var a = new Date(d.day + 'T00:00:00'), b = new Date(DAY + 'T00:00:00');
    return Math.max(1, Math.round((b - a) / 86400000));
  }
  function deadSt(d) { return d.done ? 'done' : (d.rnd > 1 ? 'rerun' : 'wait'); }
  function deadOpenN() { return DEAD ? DEAD.filter(function (d) { return !d.done; }).length : 0; }
  function todayRisk() {
    return PERF.filter(function (r) { var s = stOf(r); return s === 'wait' || s === 'draft'; });
  }

  function seed() {
    PERF = JSON.parse(JSON.stringify(DATA.perf.rows));
    PERF.forEach(function (r) {
      var pool = VOTERS.filter(function (n) { return n !== byOf(r); });
      var need = pool.length;
      if (byOf(r) === '1002' && Number(r.a) === 10) r.v = pool.filter(function (n) { return n !== '1003'; }).slice(0, 1);
      else if (r.vn >= need) r.v = pool.slice();
      else r.v = pool.filter(function (n) { return n !== meNo(); }).slice(0, r.vn);
      r.rj = r.rj || [];
    });
  }

  var DR_NOCONTACT = ['未接通', '空号', '未面访成功'];

  /* —— 本日回访（首件）：6 户 ＝ 已回访 4 ＋ 待回访 2 —— */
  var DR_VISITS = [
    {t:'10:12', n:'陈××', biz:'转存后满意度回访 · 确认资金已续存', way:'电话', stat:'已接通', fx:'良好', next:'10-21 上午', by:'赵××'},
    {t:'10:40', n:'吴××', biz:'大额存单意向跟进 · 未定存',       way:'电话', stat:'未接通', fx:'',     next:'10-17 下午', by:'赵××'},
    {t:'11:05', n:'孙××', biz:'定期开户后回访 · 问满意度',        way:'电话', stat:'已接通', fx:'良好', next:'10-26 上午', by:'赵××'},
    {t:'14:20', n:'郑××', biz:'理财到期提醒 · 提前告知',          way:'微信', stat:'已接通', fx:'一般', next:'',           by:'孙××'},
    {t:'—',     n:'刘××', biz:'转存后确认资金已续存',              way:'电话', stat:'待回访', fx:'',     next:'今日到期',   by:'钱××'},
    {t:'—',     n:'周××', biz:'理财到期提醒 · 提前 3 日告知',      way:'短信', stat:'待回访', fx:'',     next:'10-20 到期', by:'钱××'}
  ];

  /* —— 预约业务（第二件：证明这套机制不只服务一个报表）—— */
  var DR_APPTS = [
    {t:'09:15', n:'郑××', biz:'理财到期赎回转存',              src:'大堂代约', st:'今日到店', by:'钱××'},
    {t:'10:30', n:'陈××', biz:'定期存款到期转存 · 20,000 元',   src:'电话预约', st:'今日到店', by:'赵××'},
    {t:'15:31', n:'吴××', biz:'大额存单咨询 · 50 万元起',       src:'线上预约', st:'今日到店', by:'钱××'},
    {t:'15:44', n:'李××', biz:'定期存款到期转存（三年期）',      src:'线上预约', st:'今日到店', by:'钱××'},
    {t:'16:20', n:'孙××', biz:'定期存款开户 · 50,000 元',        src:'电话预约', st:'今日到店', by:'赵××'},
    {t:'—',     n:'钱××', biz:'理财转存 · 到期提醒',            src:'线上预约', st:'待到店',   by:'钱××'},
    {t:'—',     n:'周××', biz:'理财到期提醒 · 提前 3 日告知',    src:'电话预约', st:'待到店',   by:'孙××'},
    {t:'—',     n:'刘××', biz:'转存后确认 · 资金续存',          src:'大堂代约', st:'待到店',   by:'钱××'},
    {t:'—',     n:'吴××', biz:'大额存单认购 · 30 万元',         src:'线上预约', st:'待到店',   by:'赵××'}
  ];

  function drStCls(stat){
    if(stat === '待回访' || stat === '待到店' || DR_NOCONTACT.indexOf(stat) >= 0){ return 'dr-st-wait'; }
    return 'dr-st-ok';
  }
  function drillTeller(){ return {
    visit: {
      title:'本日回访报表 · 明细', sub:'本人口径 · 更新于 15:47', icon:'g-phone',
      lead:'今天该回访 <b>6 户</b>：已回访 4、待回访 2，另有 1 户没接通（不计效果）。看这张表是为了知道<b>还差谁</b>，不是算完成率。',
      kpi:[['已回访','4','户'],['待回访','2','户'],['未接通','1','户']],
      cols:['时间','客户','回访事项','方式','状态','效果','下次回访','经办'],
      rows: DR_VISITS.map(function(v){
        return [v.t, '<b>' + v.n + '</b>', v.biz, v.way,
                '<span class="dr-st ' + drStCls(v.stat) + '">' + v.stat + '</span>',
                v.fx || '<span class="dim">未接触上 · 不计</span>',
                v.next || '<span class="dim">近期无须</span>', v.by];
      }),
      note:'⭐ 「<b>未接通 / 空号 / 未面访成功</b>」不计回访效果 —— 没接触上就没有「效果」可言（与回访单同一条口径）。' +
           '回访是一个<b>动作</b>，结果要<b>记一笔</b>才算数。',
      goto:1
    },
    appt: {
      title:'本日预约业务报表 · 明细', sub:'网点口径 · 更新于 15:47', icon:'g-cal',
      lead:'今天预约 <b>9 笔</b>：到店 5、还没到 4。预约记的是<b>意向</b>，到没到店是另一件事，两个数各说各的，别当成同一个。',
      kpi:[['今日到店','5','笔'],['待到店','4','笔'],['合计','9','笔']],
      cols:['预约时段','客户','拟办业务','预约来源','状态','受理台席'],
      rows: DR_APPTS.map(function(v){
        return [v.t, '<b>' + v.n + '</b>', v.biz, v.src,
                '<span class="dr-st ' + drStCls(v.st) + '">' + v.st + '</span>', '01 号台'];
      }),
      note:'⭐ 预约与到店是<b>两个时点</b>：这里记的是<b>预约那一刻</b>填报的意向，' +
           '到店后由大堂经理当面核对、登记为<b>实际待办</b>（同一客户两处口径不同，不是矛盾）。'
    },
    /* ── 第 118 刀补齐：主页其余报表全部可点（加一张可点报表 ＝ 往表里加一条）── */
    arrive: {
      title:'本台经接到访报表 · 明细', sub:'01 号台口径 · 本台经接 · 更新于 15:47', icon:'g-users',
      lead:'今天进店 <b>31 人</b>：已办结 22、办理中 5、待办 4。这里只列最近 12 位、按时间倒序 —— <b>表短不代表人少</b>。',
      kpi:[['已办结','22','人'], ['办理中','5','人'], ['待办理','4','人']],
      cols:['时间', '客户', '办理事项', '来源', '状态', '台席'],
      rows:[
        ['15:45', '<b>陈××</b>', '定期存款转存', '电话预约', '<span class="dr-st dr-st-wait">办理中</span>', '01 号台'],
        ['15:35', '<b>吴××</b>', '理财到期赎回转存', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['15:30', '<b>孙××</b>', '大额存单认购', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['15:17', '<b>郑××</b>', '社保参保证明', '到店即办', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['15:08', '<b>钱××</b>', '寄递包裹', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:56', '<b>刘××</b>', '新开卡', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:49', '<b>周××</b>', '定期存款转存', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:34', '<b>李××</b>', '理财到期赎回转存', '到店即办', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:26', '<b>王××</b>', '大额存单认购', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:15', '<b>张××</b>', '社保参保证明', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:09', '<b>赵××</b>', '寄递包裹', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['13:55', '<b>冯××</b>', '新开卡', '到店即办', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台']
      ],
      note:'⭐ 共 <b>31</b> 人（含未预约到店与预约到店），此处按时间倒序列示最近 12 位。「到访」是客户<b>进店</b>这个动作；到没到店与办没办完是两件事。'
    },
    biz: {
      title:'本台办理业务报表 · 明细', sub:'01 号台口径 · 按笔计 · 更新于 15:47', icon:'g-grid',
      lead:'今天办了 <b>23 笔</b>：代理金融 14、邮政营业 6、综合受理 3。笔按笔算，<b>不与「人」相加</b> —— 一个人可能办三笔。',
      kpi:[['代理金融','14','笔'], ['邮政营业','6','笔'], ['综合受理','3','笔']],
      cols:['时间', '客户', '业务事项', '类别', '金额', '状态', '台席'],
      rows:[
        ['15:46', '<b>陈××</b>', '定期存款转存', '代理金融', '20,000 元', '<span class="dr-st dr-st-wait">办理中</span>', '01 号台'],
        ['15:24', '<b>吴××</b>', '定期存款开户', '代理金融', '50,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['15:16', '<b>孙××</b>', '新开卡', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:50', '<b>郑××</b>', '理财到期赎回转存', '代理金融', '8,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:38', '<b>钱××</b>', '理财认购', '代理金融', '120,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['14:08', '<b>刘××</b>', '报刊订阅', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['13:52', '<b>周××</b>', '手机银行签约', '代理金融', '20,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['13:31', '<b>李××</b>', '信用卡还款', '代理金融', '50,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['13:24', '<b>王××</b>', '新开卡', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['12:57', '<b>张××</b>', '定期存款开户', '代理金融', '8,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['12:44', '<b>赵××</b>', '大额存单认购', '代理金融', '120,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['12:27', '<b>冯××</b>', '报刊订阅', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['11:59', '<b>何××</b>', '理财认购', '代理金融', '20,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['11:48', '<b>许××</b>', '活期开户', '代理金融', '50,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['11:24', '<b>罗××</b>', '新开卡', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['11:05', '<b>高××</b>', '信用卡还款', '代理金融', '8,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['10:56', '<b>陈××</b>', '定期存款转存', '代理金融', '120,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['10:25', '<b>吴××</b>', '报刊订阅', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['10:10', '<b>孙××</b>', '大额存单认购', '代理金融', '20,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['09:48', '<b>郑××</b>', '理财到期赎回转存', '代理金融', '50,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['09:40', '<b>钱××</b>', '新开卡', '邮政营业', '—', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['09:14', '<b>刘××</b>', '活期开户', '代理金融', '8,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台'],
        ['09:02', '<b>周××</b>', '手机银行签约', '代理金融', '120,000 元', '<span class="dr-st dr-st-ok">已办结</span>', '01 号台']
      ],
      note:'⭐ 一笔 ＝ 一次业务办结登记，按时间倒序；跨条线按笔计。「办理业务数量」与「到访客户数量」<b>不是一回事</b> —— 一位客户可以办两笔，一笔也可以由他人代办。'
    },
    saveIn: {
      title:'条线新增储蓄报表 · 明细', sub:'金融条线口径 · 当日新进资金 · 更新于 15:47', icon:'g-coins',
      lead:'今天新进 <b>128.5 万</b>：定期 86.0、活期 30.5、理财 12.0。只记<b>当日新进</b>，网点内转存不重复计；三个人 64.0 ＋ 42.0 ＋ 22.5 就是这一批。',
      kpi:[['定期','86.0','万元'], ['活期','30.5','万元'], ['理财','12.0','万元']],
      cols:['时间', '客户', '类型', '金额', '存期', '经办'],
      rows:[
        ['15:44', '<b>冯××</b>', '理财', '12.0 万元', '90 天', '钱××'],
        ['15:18', '<b>王××</b>', '活期', '8.0 万元', '—', '赵××'],
        ['14:52', '<b>周××</b>', '活期', '10.0 万元', '—', '孙××'],
        ['14:05', '<b>李××</b>', '活期', '12.5 万元', '—', '孙××'],
        ['13:40', '<b>郑××</b>', '定期', '10.0 万元', '二年期', '钱××'],
        ['11:12', '<b>吴××</b>', '定期', '20.0 万元', '三年期', '钱××'],
        ['10:06', '<b>孙××</b>', '定期', '26.0 万元', '一年期', '赵××'],
        ['09:24', '<b>陈××</b>', '定期', '30.0 万元', '三年期', '赵××']
      ],
      note:'⭐ 只记<b>当日新进</b>，按时间倒序；同一笔资金在网点内转存<b>不重复计</b>（如定期到期续存算原笔、不算新增）。'
    },
    saveOut: {
      title:'条线流失储蓄报表 · 明细', sub:'金融条线口径 · 需关注 · 更新于 15:47', icon:'g-down',
      lead:'今天流出 <b>36.2 万</b>：转出他行 21.2、到期未续 15.0。这张表是<b>给自己看的</b>，不对外 —— 它记的是「还能不能挽回来」。',
      kpi:[['转出他行','21.2','万元'], ['到期未续','15.0','万元'], ['合计','36.2','万元']],
      cols:['时间', '客户', '类型', '金额', '去向 / 到期', '备注'],
      rows:[
        ['15:07', '<b>高××</b>', '到期未续', '7.0 万元', '到期日 10-16', '已电话挽留 · 待跟进'],
        ['13:22', '<b>许××</b>', '到期未续', '8.0 万元', '到期日 10-16', '客户称再考虑'],
        ['11:33', '<b>刘××</b>', '转出他行', '9.2 万元', '转入××银行', '大额取现'],
        ['09:51', '<b>钱××</b>', '转出他行', '12.0 万元', '转入××银行', '客户已被他行高息吸引']
      ],
      note:'⭐ 流失口径以<b>资金离开本网点</b>为准，按时间倒序；「到期未续」当日未续的记在当日，次日续存则从流失表撤下 —— 这张表是<b>给我们自己看的</b>，不对外。'
    },
    task: {
      title:'本日待办报表 · 明细', sub:'个人口径 · 当日 5 件 · 更新于 15:47', icon:'g-task',
      lead:'今天 <b>5 件</b>待办：已完成 2、未处理 3。未办的排前面（截止早的在前）；日终没做完的会进对账，不会悄悄消失。',
      kpi:[['已完成','2','件'], ['未处理','3','件'], ['合计','5','件']],
      cols:['待办事项', '来源', '截止', '状态', '经办'],
      rows:[
        ['客户信息补录 2 户（缺家庭住址）', '系统生成', '今日日终', '<span class="dr-st dr-st-wait">待办理</span>', '赵××'],
        ['他行转出挽留回拨（钱××）', '系统生成', '明日 10:00', '<span class="dr-st dr-st-wait">待办理</span>', '钱××'],
        ['大额存单意向跟进（吴×× · 50 万起）', '本人登记', '今日 17:30', '<span class="dr-st dr-st-wait">待办理</span>', '赵××'],
        ['定期到期提醒 3 户（陈×× / 孙×× / 吴××）', '系统生成', '今日 17:00', '<span class="dr-st dr-st-ok">已办结</span>', '赵××'],
        ['回访到期客户 2 户（刘×× / 周××）', '系统生成', '今日 17:00', '<span class="dr-st dr-st-ok">已办结</span>', '赵××']
      ],
      note:'⭐ 未办的排在前（截止早的在前）；待办<b>随岗</b>不随人 —— 换了台席，未办结的待办跟着台席走（承册子「数据归属规则」）。日终未完成的会进日终对账。'
    },
    rate: {
      title:'事项办成率报表 · 明细', sub:'金融条线口径 · 转人工记录 · 更新于 15:47', icon:'g-check',
      lead:'42 件受理里 <b>37 件一次办成</b>、5 件转了人工。转人工<b>不是失败</b> —— 要看的是「因为什么」转，不是比例本身高低。',
      kpi:[['受理事项','42','件'], ['一次办成','37','件'], ['转人工','5','次']],
      cols:['时间', '客户', '事项', '转人工原因', '处置'],
      rows:[
        ['15:29', '<b>何××</b>', '信用卡额度异议', '非本网点业务范围', '引导至客服热线'],
        ['14:36', '<b>王××</b>', '他行转入收款账户', '需临柜核验', '转 01 号台人工办理'],
        ['13:55', '<b>李××</b>', '大额存单认购', '超单笔授权额度', '转支局经理授权'],
        ['11:47', '<b>周××</b>', '社保参保证明打印', '需核对参保地', '转邮政营业窗口'],
        ['10:18', '<b>郑××</b>', '理财赎回后转存', '需人工确认赎回金额', '转 01 号台人工办理']
      ],
      note:'⭐ 办成率 ＝ 一次办成 ÷ 受理事项 ＝ 37 ÷ 42 ＝ <b>88%</b>；下表按时间倒序列出全部转人工记录。转人工<b>不等于失败</b> —— 它记的是「模型没把握、交给谁」这条链路；要看的不是数字高低，而是<b>因为什么</b>转出去。'
    }
  }; }

  function drillHall(){ return {
    visit: {
      title:'本日回访报表 · 明细', sub:'网点口径 · 更新于 15:47', icon:'g-phone',
      lead:'今天该回访 <b>6 户</b>：已回访 4、待回访 2，另有 1 户没接通（不计效果）。看这张表是为了知道<b>还差谁</b>，不是算完成率。',
      kpi:[['已回访','4','户'],['待回访','2','户'],['未接通','1','户']],
      cols:['时间','客户','回访事项','方式','状态','效果','下次回访','经办'],
      rows: DR_VISITS.map(function(v){
        return [v.t, '<b>' + v.n + '</b>', v.biz, v.way,
                '<span class="dr-st ' + drStCls(v.stat) + '">' + v.stat + '</span>',
                v.fx || '<span class="dim">未接触上 · 不计</span>',
                v.next || '<span class="dim">近期无须</span>', v.by];
      }),
      note:'⭐ 「<b>未接通 / 空号 / 未面访成功</b>」不计回访效果 —— 没接触上就没有「效果」可言（与回访单同一条口径）。' +
           '回访是一个<b>动作</b>，结果要<b>记一笔</b>才算数。',
      goto:1
    },
    appt: {
      title:'本日预约业务报表 · 明细', sub:'网点口径 · 更新于 15:47', icon:'g-cal',
      lead:'今天预约 <b>9 笔</b>：到店 5、还没到 4。预约记的是<b>意向</b>，到没到店是另一件事，两个数各说各的，别当成同一个。',
      kpi:[['今日到店','5','笔'],['待到店','4','笔'],['合计','9','笔']],
      cols:['预约时段','客户','拟办业务','预约来源','状态','受理台席'],
      rows: DR_APPTS.map(function(v){
        return [v.t, '<b>' + v.n + '</b>', v.biz, v.src,
                '<span class="dr-st ' + drStCls(v.st) + '">' + v.st + '</span>', '01 号台'];
      }),
      note:'⭐ 预约与到店是<b>两个时点</b>：这里记的是<b>预约那一刻</b>填报的意向，' +
           '到店后由大堂经理当面核对、登记为<b>实际待办</b>（同一客户两处口径不同，不是矛盾）。'
    },
    /* ── 第 118 刀补齐：主页其余报表全部可点（加一张可点报表 ＝ 往表里加一条）── */
    arrive: {
      title:'本日到访客户报表 · 明细', sub:'厅堂口径 · 全店到访全量 · 更新于 15:47', icon:'g-users',
      kpi:[['已办结','79','人'], ['办理中','8','人'], ['待办理','4','人']],
      cols:['时间', '客户', '事项', '来源', '状态', '去向'],
      rows:[
        ['15:38', '<b>陈××</b>', '定期存款转存', '电话预约', '<span class="dr-st dr-st-wait">办理中</span>', '代理金融'],
        ['15:28', '<b>吴××</b>', '社保参保证明', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>', '邮政营业'],
        ['15:23', '<b>孙××</b>', '寄递包裹', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>', '自助机'],
        ['15:10', '<b>郑××</b>', '理财咨询', '到店即办', '<span class="dr-st dr-st-ok">已办结</span>', '代理金融'],
        ['15:01', '<b>钱××</b>', '新开卡', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>', '代理金融'],
        ['14:49', '<b>刘××</b>', '转账汇款', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>', '邮政营业'],
        ['14:42', '<b>周××</b>', '定期存款转存', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>', '自助机'],
        ['14:27', '<b>李××</b>', '社保参保证明', '到店即办', '<span class="dr-st dr-st-ok">已办结</span>', '代理金融'],
        ['14:19', '<b>王××</b>', '寄递包裹', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>', '代理金融'],
        ['14:08', '<b>张××</b>', '理财咨询', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>', '邮政营业'],
        ['14:02', '<b>赵××</b>', '新开卡', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>', '自助机'],
        ['13:48', '<b>冯××</b>', '转账汇款', '到店即办', '<span class="dr-st dr-st-ok">已办结</span>', '代理金融']
      ],
      note:'⭐ 共 <b>91</b> 人（含未预约到店），此处按时间倒序列示最近 12 位。厅堂看的是<b>全量</b> —— 不按台席切分（网点所有人看的是同一份底数）。'
    },
    wait: {
      title:'平均等候时长报表 · 明细', sub:'厅堂口径 · 按小时段 · 更新于 15:47', icon:'g-clock',
      kpi:[['当前等候','4','位'], ['平均等候','6.2','分钟'], ['最长等候','11','分钟']],
      cols:['时段', '取号', '平均等候', '最长等候', '叫号完成'],
      rows:[
        ['15:30–16:30', '5 位', '8.2 分钟', '14 分钟', '5 位'],
        ['14:30–15:30', '8 位', '7.6 分钟', '12 分钟', '8 位'],
        ['13:30–14:30', '12 位', '7.2 分钟', '13 分钟', '12 位'],
        ['11:00–12:00', '9 位', '5.4 分钟', '10 分钟', '9 位'],
        ['10:00–11:00', '14 位', '6.1 分钟', '11 分钟', '14 位'],
        ['09:00–10:00', '11 位', '4.8 分钟', '9 分钟', '11 位']
      ],
      note:'⭐ 等候时长<b>从取号算起、到叫号为止</b>（不含办理时长）；时段按由近及远排。看这张表是为了知道<b>哪个时段要加人</b> —— 下午三点后等候抬头的，多半是窗口在换班。'
    },
    apptRate: {
      title:'预约到店率报表 · 明细', sub:'厅堂口径 · 预约 9 · 实际到店 5 · 更新于 15:47', icon:'g-cal',
      kpi:[['预约','9','笔'], ['到店','5','笔'], ['到店率','56%','']],
      cols:['预约时段', '客户', '拟办业务', '预约来源', '状态'],
      rows:[
        ['16:40', '<b>周××</b>', '理财到期提醒', '电话预约', '<span class="dr-st dr-st-wait">未到店</span>'],
        ['16:20', '<b>钱××</b>', '理财转存', '线上预约', '<span class="dr-st dr-st-wait">未到店</span>'],
        ['15:44', '<b>冯××</b>', '定期存款到期转存', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['15:31', '<b>吴××</b>', '大额存单咨询', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['15:00', '<b>孙××</b>', '定期存款开户', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['14:00', '<b>刘××</b>', '社保参保证明', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['11:20', '<b>李××</b>', '社保参保证明', '线上预约', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['10:30', '<b>陈××</b>', '定期存款到期转存', '电话预约', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['09:15', '<b>郑××</b>', '理财到期赎回转存', '大堂代约', '<span class="dr-st dr-st-ok">已办结</span>']
      ],
      note:'⭐ 到店率 ＝ 实际到店 ÷ 预约 ＝ 5 ÷ 9 ＝ <b>56%</b>；<b>未到店的排在最上</b>——先看没来的。到期没来的由大堂经理回访追一次（回访单里记「预约办理业务」那条路）。'
    },
    flow: {
      title:'分流成功率报表 · 明细', sub:'厅堂口径 · 引导 29 次 · 更新于 15:47', icon:'g-flow',
      kpi:[['引导分流','29','次'], ['转台席','4','次'], ['成功率','86%','']],
      cols:['时间', '客户', '需求', '引导去向', '结果'],
      rows:[
        ['14:22', '<b>高××</b>', '社保参保证明', '代理金融 · 转错，改送邮政营业', '<span class="dr-st dr-st-wait">转台席</span>'],
        ['11:16', '<b>王××</b>', '社保参保证明', '邮政营业 · 04 号台', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['10:52', '<b>周××</b>', '寄递包裹', '邮政营业 · 04 号台', '<span class="dr-st dr-st-ok">已办结</span>'],
        ['09:38', '<b>吴××</b>', '大额存单咨询', '代理金融 · 01 号台', '<span class="dr-st dr-st-ok">已办结</span>']
      ],
      note:'⭐ 分流成功率 ＝ 一次引导到位 ÷ 引导总次 ＝ 25 ÷ 29 ＝ <b>86%</b>；下表按时间倒序列出全部转台席记录。转台席记的是<b>我们引导错了</b>，不是客户的错 —— 这张表是给自己找毛病的。'
    },
    task: {
      title:'本日待办报表 · 明细', sub:'个人口径 · 当日 5 件 · 更新于 15:47', icon:'g-task',
      kpi:[['已完成','2','件'], ['未处理','3','件'], ['合计','5','件']],
      cols:['待办事项', '来源', '截止', '状态', '经办'],
      rows:[
        ['厅堂物料补充（取号纸 / 单据）', '本人登记', '今日日终', '<span class="dr-st dr-st-wait">待办理</span>', '孙××'],
        ['台席换班交接（01 / 02 号台）', '系统生成', '今日 17:30', '<span class="dr-st dr-st-wait">待办理</span>', '孙××'],
        ['自助机 C 巡检（维护中）', '本人登记', '今日 16:00', '<span class="dr-st dr-st-wait">待办理</span>', '孙××'],
        ['预约未到店客户回拨 2 户（钱×× / 周××）', '系统生成', '今日 17:00', '<span class="dr-st dr-st-ok">已办结</span>', '孙××'],
        ['厅堂等候超 10 分钟客户安抚（2 位）', '系统生成', '实时', '<span class="dr-st dr-st-ok">已办结</span>', '孙××']
      ],
      note:'⭐ 未办的排在前（截止早的在前）；待办<b>随岗</b>不随人 —— 换了班，未办结的待办跟着岗位走（承册子「数据归属规则」）。'
    },
    rate: {
      title:'事项办成率报表 · 明细', sub:'厅堂口径 · 转人工记录 · 更新于 15:47', icon:'g-check',
      kpi:[['受理事项','40','件'], ['一次办成','36','件'], ['转人工','3','次']],
      cols:['时间', '客户', '事项', '转人工原因', '处置'],
      rows:[
        ['15:12', '<b>何××</b>', '理财风险评估', '客户风险等级待复核', '转 01 号台人工办理'],
        ['11:41', '<b>罗××</b>', '对公开户咨询', '非本网点业务', '转支局经理接待'],
        ['10:07', '<b>郑××</b>', '大额取现预约', '超当日库存', '转支局经理核库']
      ],
      note:'⭐ 办成率 ＝ 36 ÷ 40 ＝ <b>90%</b>；下表按时间倒序列出全部转人工记录。转人工<b>不等于失败</b> —— 它记的是「模型没把握、交给谁」这条链路。'
    }
  }; }

  function bindMe(no) {
    SESSION_NO = no || '';
    var row = STAFF.filter(function (s) { return s.no === SESSION_NO; })[0];
    if (!row) {
      ME = { no: SESSION_NO, name: '', missing: true };
      return false;
    }
    ME = { no: row.no, name: row.name, missing: false };
    return true;
  }
  function rebuildVoters() {
    VOTERS = STAFF.filter(voterRow).map(function (s) { return s.no; });
  }
  function use(role) {
    ROLE = role || 'P1';
    if (arguments.length > 1) bindMe(arguments[1]);
    else if (!ME || ME.missing) bindMe(SESSION_NO);
    SCOPE = (role === 'P2' || role === 'P3' || role === 'P4') ? 'mine' : 'net';
    seed();
    var pack = DATA.counts.rows[role] || DATA.counts.rows.P1;
    var deadN = pack.dead;
    DEAD = [];
    for (var i = 0; i < deadN; i++) {
      DEAD.push({
        day: shiftDay(DAY, -(6 - i)), t: '16:0' + i, by: ['钱××', '赵××', '孙××'][i % 3],
        k: '定期', a: 6 + i, note: '日终未凑齐全票', got: 2, need: 6, rnd: 1, miss: ['王××', '赵××'], done: 0
      });
    }
    var winN = pack.win;
    HALL.windows = [];
    for (var w = 0; w < winN; w++) {
      HALL.windows.push({ cls: w ? 'busy' : 'free', no: '0' + (w + 1), st: w ? '办理中' : '空闲', line: '柜面', who: ['赵××', '钱××', '孙××'][w] || '—', t: (4 + w) + ' 分钟' });
    }
    HALL.kiosks = ROLE === 'P4'
      ? [{ cls: 'free', no: '自助1', st: '空闲', who: '—', t: '—' }, { cls: 'busy', no: '自助2', st: '使用中', who: '—', t: '—' }, { cls: 'free', no: '自助3', st: '维护中', who: '—', t: '—' }]
      : [{ cls: 'free', no: '自助1', st: '空闲', who: '—', t: '—' }];
    var qn = pack.queue;
    HALL.queue = [];
    for (var q = 0; q < qn; q++) HALL.queue.push({ no: 'A0' + (q + 1), item: '存取', wait: (3 + q) + ' 分钟', to: '01' });
    var an = pack.appt;
    HALL.appts = [];
    for (var a = 0; a < an; a++) HALL.appts.push({ cls: '', t: '1' + a + ':00', who: ['周××', '冯××', '李××', '孙××'][a], item: '代理金融', st: a ? '待到店' : '已到店' });
    HALL.tablet = {
      acts: [['g-scan', '扫码', role + ' 入口'], ['g-cal', '预约', an + ' 笔']],
      note: role + ' · 等候 ' + qn + ' 位'
    };
    DRILL = role === 'P4' ? drillHall() : drillTeller();
    if (ROLE === 'P4') {
      HALL.appts = DR_APPTS.map(function (v) {
        return { t: v.t, who: v.n, item: v.biz, src: v.src, st: v.st === '今日到店' ? '已到店' : '待到店', cls: '' };
      });
      var todo = HALL_TASK.filter(function (t) { return t.st !== '已办结'; }).length;
      HALL.tablet = {
        acts: [['g-task', '待办', todo + ' 笔'], ['g-cal', '预约', DR_APPTS.length + ' 笔'], ['g-users', '等候', HALL.queue.length + ' 人']],
        note: '待办、预约、等候都按现在的记录数'
      };
    }
    paintEntry();
    paintP4();
  }
  function paintP4() {
    var board = $('v10Board');
    var home = $('p4home');
    if (ROLE !== 'P4') { if (home) home.hidden = true; return; }
    mount();
    board = $('v10Board');
    if (!board) return;
    if (!home) {
      home = document.createElement('div');
      home.id = 'p4home';
      board.parentNode.insertBefore(home, board);
    }
    home.hidden = false;
    if (!$('quickrow')) {
      var q = document.createElement('div');
      q.id = 'quickrow';
      q.innerHTML = ['识别客户', '为客户取号', '查看预约', '厅堂巡检'].map(function (t) {
        return '<button type="button" data-jump="' + t + '">' + t + '</button>';
      }).join('');
      home.appendChild(q);
    }
    var slots = $('p4slots');
    if (!slots) {
      slots = document.createElement('div');
      slots.id = 'p4slots';
      home.appendChild(slots);
    }
    ['win', 'queue', 'appt'].forEach(function (part) {
      var n = document.querySelector('[data-part="' + part + '"]');
      if (n) slots.appendChild(n);
    });
    if (!$('p4wait')) {
      var w = document.createElement('section');
      w.id = 'p4wait';
      w.innerHTML = '<h3>厅堂取号时段分布</h3><p>按小时 · 单位：人次（取号口径）</p><div id="p4bars"></div>';
      home.appendChild(w);
    }
    var tab = document.querySelector('[data-part="tab"]');
    if (tab) home.appendChild(tab);
    var perf = $('v10Perf');
    if (perf) { perf.hidden = false; home.appendChild(perf); }
    var rows = (DRILL.wait && DRILL.wait.rows) || [];
    var bars = $('p4bars');
    if (bars) {
      bars.innerHTML = rows.length
        ? '<table><tr><th>时段</th><th>取号数</th><th>平均等候</th><th>最长等候</th></tr>' +
          rows.map(function (r) {
            return '<tr><td>' + r[0] + '</td><td>' + r[1] + '</td><td>' + r[2] + '</td><td>' + r[3] + '</td></tr>';
          }).join('') + '</table>'
        : '当前无人等候';
    }
    renderHall();
    renderQueue();
    renderAppt();
    renderTablet();
    renderClear();
  }

  /* 原型/05_普通柜员页.html L2664 · 09_大堂经理页.html L2874 同文 */
  function renderClear(){
    var list = scopeRows();
    if (isMine() && !list.length) {
      $('pfLead').innerHTML = '今天没有记在你名下的业绩。';
      $('pfClearK').innerHTML = '';
      $('pfClearCnt').innerHTML = '';
      $('pfClearList').innerHTML = '<p>你是邮政营业岗，业绩按「件」记；今天全支局 ' + PERF.length +
        ' 笔都是代理金融（万元），收寄 ' + sumN(MAIL, 'n') +
        ' 件的明细在「日终结算」里，那 ' + sumN(MAIL, 'n') +
        ' 件按台席记，不按人记。要查某个人的业绩，去「网点确认」按人分栏看。</p>';
      $('pfClearNote').innerHTML = '';
      return;
    }
    var c = counts(list);
    var ml = list.filter(function(r){ return r.u === 'money'; });
    var pl = list.filter(function(r){ return r.u === 'piece'; });
    var totM = sumOf(ml), totP = sumOf(pl);
    var chN = {};
    list.forEach(function(r){ if(r.ch) chN[r.ch] = (chN[r.ch] || 0) + 1; });
    var chTxt = Object.keys(chN).map(function(k){ return k + ' ' + chN[k]; }).join(' · ');

    if(isMine()){
      $('pfLead').innerHTML = '这一页回答「<b>今天哪几位客户是我的、我促成了多少</b>」。' +
        '只算<b>你名下</b>的 ' + list.length + ' 笔 —— 网点的整本账在支局经理那儿，不在这儿再算一遍。' +
        '大堂经理的业绩<b>记在客户身上</b>：走访出来的、电话唤醒的、厅堂转介来的，都算你的。' +
        '<span class="dim">客户只显示姓与尾号，全名在客户档案里。</span>';
    } else {
      var mineL = PERF.filter(function(r){ return byOf(r) === meNo(); });
      var mineTxt = mineL.length
        ? '其中 <b>' + mineL.length + ' 条</b>算到你头上（' +
          (mineL[0].u === 'piece' ? sumOf(mineL) + ' 件' : f1(sumOf(mineL)) + ' 万元') + '）。'
        : '今天这 ' + PERF.length + ' 条里<b>没有你经办的</b> —— 你在这页看的是全网点的账。';
      $('pfLead').innerHTML = '这一页回答「<b>今天哪几笔算到我头上、确认到哪一步了</b>」。' + mineTxt +
        '每笔要<b>其余 ' + (VOTERS.length - 1) + ' 人全部通过</b>才算完成 —— 全网点 ' + VOTERS.length +
        ' 人可投票，扣掉经办人自己就是 ' + (VOTERS.length - 1) + ' 票。';
    }

    if(isMine()){
      $('pfClearK').innerHTML =
        box('我的客户单', list.length, '笔') +
        box('我促成金额', ml.length ? f1(totM) : '0.0', '万元' + (ml.length ? '' : ' · 本条线无')) +
        box('客户来源', Object.keys(chN).length, '种来源', '', chTxt || '—') +
        box('确认进度', c.ok + '/' + list.length, '笔全票', (c.wait || c.draft) ? 'warn' : '');
    } else {
      $('pfClearK').innerHTML =
        box('今日条数', PERF.length, '条') +
        box('代理金融', ml.length ? f1(totM) : '0.0', '万元' + (ml.length ? '' : ' · 本条线无')) +
        box('邮政营业', pl.length ? totP : 0, '件' + (pl.length ? '' : ' · 本条线无')) +
        box('全票通过', c.ok, '条 / 待确认 ' + c.wait + (c.draft ? ' · 待核对 ' + c.draft : ''), c.wait ? 'warn' : '');
    }

    $('pfClearCnt').textContent = isMine()
      ? '我的 ' + list.length + ' 笔 · 按时间倒序 · 客户只到姓与尾号'
      : '今日全部 ' + PERF.length + ' 条 · 按时间倒序 · 只记笔数与金额，不记客户信息';

    var head = isMine()
      ? '<table><tr><th>时间</th><th>种类</th><th class="num">金额（万元）</th><th>客户</th><th>来源</th>' +
        '<th>录入</th><th>状态</th><th>全票进度</th><th>我能做什么</th></tr>'
      : '<table><tr><th>时间</th><th>种类</th><th class="num">数量</th><th class="num">金额（万元）</th>' +
        '<th>来源</th><th>经办</th><th>状态</th><th>全票进度</th><th>我能做什么</th></tr>';

    $('pfClearList').innerHTML = head + list.map(function(r){
      var i = PERF.indexOf(r);
      var st = ST[stOf(r)], need = needOf(r), got = votesOf(r).length;
      var act = '';
      if(r.draft && byOf(r) === meNo()){
        act = '<button class="pf-btn" data-act="check" data-i="' + i + '">' + (isMine() ? '认领 · 核对无误' : '核对无误') + '</button>';
      } else if(r.draft){
        act = '<span class="dim">等本人核对</span>';
      } else if(stOf(r) === 'wait' && byOf(r) === meNo()){
        act = '<span class="dim">本人不能投</span>';
      } else if(stOf(r) === 'wait' && canVote(r)){
        act = '<button class="pf-btn" data-act="vote" data-i="' + i + '">投通过</button>';
      } else if(stOf(r) === 'ok'){
        act = '<span class="dim">' + (r.rj && r.rj.length ? '' : '不可改 · 可结算') + '</span>';
      } else if(stOf(r) === 'wait'){
        var miss = pendingOf(r);
        act = '<span class="dim">我已投 · 还差 ' + miss.map(function (n) { return nameOf(n); }).join('、') + '</span>';
      } else {
        act = '<span class="dim">' + esc((r.rj[0] && r.rj[0].why) || '') + '</span>';
      }
      var src = r.src === '模型' ? '<span class="src-m">模型自动</span>' : '手工';
      var mid = isMine()
        ? '<td class="num">' + (r.u === 'piece' ? '—' : f1(r.a)) + '</td>' +
          '<td class="pf-cli">' + (r.cl || '<span class="dim">待补客户</span>') + '</td>' +
          '<td>' + chTag(r.ch) + '</td>' + '<td>' + src + '</td>'
        : '<td class="num">' + (r.u === 'piece' ? r.a + '<span class="pf-unit">件</span>' : (r.q || 1) + '<span class="pf-unit">笔</span>') + '</td>' +
          '<td class="num">' + (r.u === 'piece' ? '—' : f1(r.a)) + '</td>' +
          '<td>' + src + '</td><td>' + nameOf(byOf(r)) + '</td>';
      return '<tr><td class="num" style="text-align:left">' + r.t + '</td><td>' + r.k + '</td>' + mid +
        '<td><span class="pf-st ' + st[1] + '">' + st[0] + '</span></td>' +
        '<td>' + vbar(got, need, r.draft) + '</td><td>' + act + '</td></tr>';
    }).join('') + '</table>';

    $('pfClearNote').innerHTML = '⭐ <b>模型录入不等于已入账</b>：模型按流水自动匹配，本人核对前停在「待本人核对」，' +
      '不进确认队列；核对后才开始计票。<b>核对不是重复录入</b> —— 它只回答「这笔是不是我的」。<br>' +
      '⭐ 统计口径是<b>受理即计、驳回才回冲</b>：待确认的已经算进合计，所以确认状态不影响统计页，' +
      '只影响「能不能改、能不能结算」。<br>' +
      (isMine()
        ? '⭐ <b>两本账不合并</b>：同一笔钱，柜员记「经办」、我记「客户归属」；两边都能查到，但加起来是假数。<br>'
        : '') +
      (MODE === 'both'
        ? '⭐ <b>种类下拉是全岗位的</b>：代理金融记万元、邮政营业记件。你从别的岗位调过来，' +
          '之前那条线的业绩仍然跟你走；这边代办的储蓄也记在你名下 —— <b>调岗不撕业绩</b>。'
        : '⭐ 这个下拉里同时有代理金融与邮政营业两类 —— <b>业绩随人、不随岗</b>。') +
      '<br>⭐ <b>日终 18:00 清算</b>：到点还没凑齐全票的笔会转「死账」，次日挂到支局长待办，区办公室按日通报。' +
      (DEAD ? '今天还有 <b>' + todayRisk().length + '</b> 笔没走完，<b>8 分钟</b>后清算。' : '别拖到下班才投。');
  }

  /* 原型/05_普通柜员页.html L2834 · 09 L3044 */
  function renderConfirm(){
    var by = {}, order = [];
    PERF.forEach(function(r){ var k = byOf(r); if(!by[k]){ by[k] = []; order.push(k); } by[k].push(r); });
    var mine = PERF.filter(function(r){ return byOf(r) === meNo() && stOf(r) === 'wait'; });
    var votable = PERF.filter(canVote);

    $('pfConfirmLead').innerHTML = '这一页回答「<b>谁的钱还没凑齐全票</b>」。按人分栏，<b>每一笔</b>都能单独通过或驳回；' +
      '<b>经办人不能投自己的票</b> —— 所以' + (mine.length ? '你的 ' + mine.length + ' 笔只能等别人' : '你没有待他人确认的业绩') + '。' +
      '「一键确认」只投<b>你还没投的</b>那几笔，不会替别人投票。';

    $('pfConfirmList').innerHTML = order.map(function(who){
      var list = by[who];
      var c = counts(list);
      var stTxt = [c.ok ? '全票通过 ' + c.ok : '', c.wait ? '待确认 ' + c.wait : '',
                   c.draft ? '待本人核对 ' + c.draft : '', c.rej ? '已驳回 ' + c.rej : ''].filter(Boolean).join(' · ');
      var myVotable = list.filter(canVote).length;
      var btns = '';
      if(who !== meNo() && myVotable){
        btns = '<button class="pf-btn pri" data-act="okWho" data-who="' + who + '">全部投通过 · ' + myVotable + ' 笔</button>';
      } else if(who === meNo()){
        btns = '<span class="dim">经办人 · 不可自投</span>';
      } else if(who !== meNo() && c.wait){
        btns = '<span class="dim">你已投过这些笔</span>';
      }
      return '<div class="pf-grp"><div class="pf-gh"><span class="who">' + nameOf(who) + '</span>' +
        '<span class="sub">' + stTxt + ' · 合计 ' + (list[0].u === 'piece' ? sumOf(list) + ' 件' : f1(sumOf(list)) + ' 万元') +
        ' / ' + list.length + ' 条</span><span class="sp"></span>' + btns + '</div>' +
        '<table><tr><th>时间</th><th>种类</th><th class="num">数量</th><th class="num">金额</th><th>来源</th>' +
        '<th>状态</th><th>票数</th><th style="text-align:right">逐笔</th></tr>' +
        list.map(function(r){
          var i = PERF.indexOf(r), st = ST[stOf(r)], got = votesOf(r).length, need = needOf(r);
          var act = '';
          if(canVote(r)){
            act = '<span class="pf-act"><button class="ok" data-act="vote" data-i="' + i + '">通过</button>' +
                  '<button class="no" data-act="rejOne" data-i="' + i + '">驳回</button></span>';
            if (REJ_I === i) {
              act += '<div>' + ['金额不符', '笔数不符', '非本人经办', '其他'].map(function (w) {
                return '<button type="button" data-act="rejWhy" data-i="' + i + '" data-why="' + w + '">' + w + '</button>';
              }).join(' ') + '</div>';
            }
          } else if(byOf(r) === meNo()){ act = '<span class="dim">本人不能投</span>'; }
          else if(rejsOf(r).length){ act = '<span class="dim">已驳回 · 待经办人更正 · ' + esc(rejsOf(r)[0].why) + '</span>'; }
          else if(stOf(r) === 'ok'){ act = '<span class="dim">已齐</span>'; }
          else if(stOf(r) === 'wait'){
            var miss = pendingOf(r);
            act = '<span class="dim">我已投 · 还差 ' + miss.map(function (n) { return nameOf(n); }).join('、') + '</span>';
          }
          return '<tr><td style="text-align:left">' + r.t + '</td><td>' + r.k + '</td>' +
            '<td class="num">' + (r.u === 'piece' ? r.a : (r.q || 1)) + '<span class="pf-unit">' + (r.u === 'piece' ? '件' : '笔') + '</span></td>' +
            '<td class="num">' + (r.u === 'piece' ? '—' : f1(r.a)) + '</td>' +
            '<td>' + (r.src === '模型' ? '<span class="src-m">模型自动</span>' : '手工') + '</td>' +
            '<td><span class="pf-st ' + st[1] + '"' + (rejsOf(r).length ? ' title="' + esc(rejsOf(r)[0].why) + '"' : '') + '>' + st[0] + '</span></td>' +
            '<td>' + vbar(got, need, r.draft) + '</td><td>' + act + '</td></tr>';
        }).join('') + '</table></div>';
    }).join('');

    $('pfConfirmNote').innerHTML = '⭐ <b>全票才算完成</b>：' + VOTERS.length + ' 人可投票，扣掉经办人是 ' + (VOTERS.length - 1) +
      ' 票；<b>缺一票都不算</b>。保安不建账号' + (OFF.length ? '、请假不计票' : '') + ' —— 否则永远凑不齐。<br>' +
      '⭐ <b>驳回不删除记录</b>：原数保留、标记「已驳回」、理由随业绩留痕，经办人更正后重新提交；' +
      '合计数不会因为驳回而消失，但「能否结算」会变。<br>' +
      '⭐ 一键确认 = <b>你一个人</b>把还没投的笔投一遍，不是替全网点点头。';

    $('pfAllN').textContent = votable.length ? ' · ' + votable.length + ' 笔' : '';
    $('pfAll').disabled = !votable.length;
    $('pfBadge').textContent = votable.length ? votable.length : '';
  }

  /* 原型/05_普通柜员页.html L3063 · 09 L3273 */
  function renderDead(){
    if(!DEAD) return;
    var open = DEAD.filter(function(d){ return !d.done; });
    var amt = 0, maxDay = 0;
    open.forEach(function(d){ amt += Number(d.a) || 0; maxDay = Math.max(maxDay, deadDays(d)); });
    var risk = todayRisk();

    $('pfDeadBar').innerHTML =
      '<svg class="ic-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><use href="#g-bell"/></svg>' +
      '<span><b>日终 18:00 清算</b> · 现在 17:52 · 距清算还有 <b>8 分钟</b></span><span class="sp"></span>' +
      '<span class="ck">区办已按日通报 2 次 · 最近 10-19 08:30</span>';

    $('pfDeadK').innerHTML =
      box('待处理死账', open.length, '笔', open.length ? 'warn' : '') +
      box('涉及金额', f1(amt), '万元') +
      box('最长挂账', maxDay, '天', maxDay > 1 ? 'warn' : '') +
      box('今日待清算', risk.length, '笔', risk.length ? 'warn' : '');

    var h = '<div class="pf-sec">前日遗留<span class="dim">已过日终 · 共 ' + DEAD.length + ' 笔</span><span class="ln"></span></div>' +
      '<table class="pf-dt"><tr><th>起账日</th><th>时间</th><th>经办</th><th>种类</th><th class="num">金额（万元）</th>' +
      '<th>死账原因</th><th>票数 / 差谁</th><th class="num">挂账</th><th style="text-align:right">处理</th></tr>' +
      DEAD.map(function(d, i){
        var st = deadSt(d);
        var tag = st === 'rerun' ? '<span class="pf-dtag warn">第 ' + d.rnd + ' 轮重投</span>'
                : (st === 'done' ? '<span class="pf-dtag done">已处理</span>' : '');
        var missTxt;
        if(d.done){
          missTxt = '<span class="dim">' + esc(d.way || '') + '</span>';
        } else if(d.draft){
          missTxt = '<span class="miss">本人没核对，' + (VOTERS.length - 1) + ' 人无从表态</span>';
        } else if(d.miss && d.miss.length){
          missTxt = '<span class="miss"><span class="who">' + d.miss.slice(0, 3).join('、') +
            (d.miss.length > 3 ? ' 等' : '') + '</span></span>';
        } else {
          missTxt = '<span class="dim">—</span>';
        }
        var act = d.done
          ? '<span class="dim">' + esc(d.at || '') + ' · ' + esc(d.why ? d.why.slice(0, 12) + '…' : '') + '</span>'
          : '<span class="pf-act">' +
            '<button class="ok" data-act="rerun" data-i="' + i + '">重新发起重投</button>' +
            '<button data-act="dc" data-i="' + i + '" data-way="裁定入账">裁定</button>' +
            '<button class="no" data-act="dc" data-i="' + i + '" data-way="退回经办人更正">退回</button></span>';
        return '<tr><td style="text-align:left">' + d.day.slice(5) + tag + '</td>' +
          '<td class="num" style="text-align:left">' + d.t + '</td><td>' + d.by + '</td><td>' + d.k + '</td>' +
          '<td class="num">' + f1(d.a) + '</td>' +
          '<td class="dim" style="max-width:210px;line-height:1.5">' + esc(d.note) + '</td>' +
          '<td><span class="pf-vt' + (d.done ? '' : ' bad') + '"><b>' + d.got + '</b>/' + d.need + '</span> ' + missTxt + '</td>' +
          '<td class="num">' + (d.done ? '—' : deadDays(d) + ' 天') + '</td><td style="text-align:right">' + act + '</td></tr>';
      }).join('') + '</table>';

    h += '<div class="pf-sec" style="margin-top:14px">今日待清算' +
      '<span class="dim">' + risk.length + ' 笔没走完 · 18:00 后自动转死账</span><span class="ln"></span></div>';
    if(risk.length){
      h += '<table class="pf-dt"><tr><th>时间</th><th>经办</th><th>种类</th><th class="num">金额（万元）</th>' +
        '<th>卡在哪</th><th>差几票</th><th style="text-align:right">现在能做</th></tr>' +
        risk.map(function(r){
          var s = stOf(r), need = needOf(r), got = votesOf(r).length;
          var stuck = s === 'draft' ? '模型录进来了，本人还没核对' : '在等 ' + pendingOf(r).length + ' 人表态';
          return '<tr><td class="num" style="text-align:left">' + r.t + '</td><td>' + nameOf(byOf(r)) + '</td><td>' + r.k + '</td>' +
            '<td class="num">' + (r.u === 'piece' ? '—' : f1(r.a)) + '</td>' +
            '<td class="dim">' + stuck + '</td>' +
            '<td><span class="pf-vt bad"><b>' + got + '</b>/' + need + '</span></td>' +
            '<td style="text-align:right"><button class="pf-btn" data-act="urge" data-i="' + PERF.indexOf(r) + '">催一下</button></td></tr>';
        }).join('') + '</table>';
    } else {
      h += '<div class="pf-empty">今天没有卡住的笔 —— 18:00 清算时不会新增死账。</div>';
    }
    $('pfDeadList').innerHTML = h;

    $('pfDeadNote').innerHTML = '⭐ <b>死账不是作废</b>：钱已经发生了，只是没人点头。出口只有三个 —— ' +
      '<b>重投</b>（重新凑票）、<b>裁定</b>（你担责，写理由）、<b>退回更正</b>（改数重报）；三个都要留痕。<br>' +
      '⭐ <b>日终不清算，次日区办公室按日通报</b>：所以这条死账同时是今天的一条待办，处理完才从待办里消失 —— ' +
      '它不会自己好。<br>' +
      '⭐ 重投<b>只重置票池</b>，不改金额、不改经办：改数必须走「退回经办人更正」，否则就是在替经办人改账。';

    var n = deadOpenN();
    $('pfDeadBadge').textContent = n || '';
    $('pfDeadTab').style.display = DEAD ? '' : 'none';
    window.__deadN = n;
    if(window.__deadRefresh) window.__deadRefresh();
  }

  /* 原型/09_大堂经理页.html L1674 */
  function renderHall(h) {
    h = h || HALL;
    $('winGrid').innerHTML = h.windows.map(function (w) {
      return '<div class="win ' + w.cls + '"><div class="w-h"><span class="w-no">' + w.no + '</span><span class="w-st">' + w.st +
        '</span></div><div class="w-line">' + w.line + '</div><div class="w-who">' + w.who + '</div><div class="w-t">' + w.t + '</div></div>';
    }).join('');
    $('kioskGrid').innerHTML = h.kiosks.map(function (k) {
      return '<div class="win ' + k.cls + '"><div class="w-h"><span class="w-no">' + k.no + '</span><span class="w-st">' + k.st +
        '</span></div><div class="w-who">' + k.who + '</div><div class="w-t">' + k.t + '</div></div>';
    }).join('');
  }
  /* 原型/09_大堂经理页.html L1691 */
  function renderQueue(h) {
    h = h || HALL;
    if (!h.queue.length) { $('queueList').innerHTML = '当前无人等候'; return; }
    $('queueList').innerHTML = h.queue.map(function (q) {
      return '<div class="qrow"><span class="q-no">' + q.no + '</span><span class="q-item">' + q.item +
        '</span><span class="q-wait">' + q.wait + '</span><span class="q-to">' + q.to + '</span><button class="q-btn">叫号</button></div>';
    }).join('');
  }
  /* 原型/09_大堂经理页.html L1703 */
  function renderAppt(h) {
    h = h || HALL;
    $('apptList').innerHTML = h.appts.map(function (a) {
      return '<div class="arow ' + a.cls + '"><span class="a-t">' + a.t + '</span><span class="a-who">' + a.who +
        '</span><span class="a-item">' + a.item + '</span>' +
        (a.src ? '<span class="a-src">' + a.src + '</span>' : '') +
        '<span class="a-st">' + a.st + '</span></div>';
    }).join('');
  }
  /* 原型/09_大堂经理页.html L1714 */
  function renderTablet(h){
    h = h || HALL;
    var tb = h.tablet;
    $('tabActs').innerHTML = tb.acts.map(function(a){
      return '<div class="tact">' + icon(a[0],'ic-sm') +
        '<div><div class="tt">' + a[1] + '</div><div class="ts">' + a[2] + '</div></div></div>';
    }).join('');
    $('tabNote').innerHTML = tb.note;
  }

  function drEl(id) { return document.getElementById(id); }
  /* 原型/09_大堂经理页.html L2051 · 05 L1843 */
  function openDrill(kind){
    var d = DRILL[kind];
    if(!d){ return; }
    drEl('drTitle').textContent = d.title;
    drEl('drSub').textContent   = d.sub || '';
    drEl('drIconUse').setAttribute('href', '#' + (d.icon || 'g-phone'));
    var body = d.lead ? '<div class="dr-lead">' + d.lead + '</div>' : '';
    if(d.kpi && d.kpi.length){
      body += '<div class="dr-k">' + d.kpi.map(function(b){
        return '<div class="box"><div class="t">' + b[0] + '</div><div class="v">' + b[1] +
               (b[2] ? '<u>' + b[2] + '</u>' : '') + '</div></div>';
      }).join('') + '</div>';
    }
    var rows = d.rows || [];
    body += rows.length
      ? '<table><tr>' + d.cols.map(function(c){ return '<th>' + c + '</th>'; }).join('') + '</tr>' +
        rows.map(function(r){
          return '<tr>' + r.map(function(c){ return '<td>' + c + '</td>'; }).join('') + '</tr>';
        }).join('') + '</table>'
      : '<div class="dr-empty">本日暂无明细。</div>';
    if(d.note){ body += '<div class="dr-note">' + d.note + '</div>'; }
    drEl('drBody').innerHTML = body;
    drEl('drGoto').style.display = d.goto ? '' : 'none';
    drEl('drModal').classList.add('on');
    drEl('drModal').setAttribute('aria-hidden', 'false');
    drEl('drMask').classList.add('on');
  }
  function closeDrill() {
    if (!drEl('drModal')) return;
    drEl('drModal').classList.remove('on');
    drEl('drModal').setAttribute('aria-hidden', 'true');
    drEl('drMask').classList.remove('on');
  }

  var bxOk = null;
  function bxEnsure() {
    var mk = document.getElementById('bxMk');
    if (!mk) {
      mk = document.createElement('div');
      mk.id = 'bxMk'; mk.className = 'bx-mk';
      document.body.appendChild(mk);
    }
    if (mk.querySelector('.bx-dlg')) return mk;
    mk.innerHTML = '<div class="bx-dlg" id="bxDlg"><div class="bx-hd"><h3 id="bxT"></h3><button class="bx-x" type="button">✕</button></div><div class="bx-bd" id="bxB"></div><div class="bx-ft" id="bxF"></div></div>';
    mk.querySelector('.bx-x').onclick = bxClose;
    mk.onclick = function (e) { if (e.target === mk) bxClose(); };
    return mk;
  }
  function bxClose() {
    var mk = document.getElementById('bxMk');
    if (mk) mk.classList.remove('on');
    bxOk = null;
  }
  /* 原型/05_普通柜员页.html L3688 */
  function bxOpen(cfg) {
    var mk = bxEnsure();
    document.getElementById('bxT').textContent = cfg.t || '';
    document.getElementById('bxB').innerHTML = cfg.body || '';
    var f = document.getElementById('bxF');
    f.innerHTML = '';
    (cfg.foot || [{ k: 'cancel', t: '关闭' }]).forEach(function (b) {
      var el = document.createElement('button');
      el.type = 'button';
      el.textContent = b.t;
      el.onclick = function () { bxClose(); };
      f.appendChild(el);
    });
    mk.classList.add('on');
  }
  /* 原型/05 L3713 · 09 L3949 */
  function bxRows(cols, head, rows){
    var h = '<div class="bx-tb" style="--cols:' + cols + '">' +
      '<div class="bx-tr bx-th">' + head.map(function(x){ return '<span>' + x + '</span>'; }).join('') + '</div>';
    rows.forEach(function(r){
      h += '<div class="bx-tr">' + r.map(function(c){ return '<span>' + c + '</span>'; }).join('') + '</div>';
    });
    return h + '</div>';
  }
  /* 原型/05 L3721 · 09 L3957 */
  function bxChain(items){
    return '<div class="bx-ch">' + items.map(function(c){
      return '<div class="bx-ci' + (c.on ? ' on' : '') + '"><div class="t">' + c.t + '</div>' +
        (c.d ? '<div class="d">' + c.d + '</div>' : '') +
        (c.b ? '<div class="b">' + c.b + '</div>' : '') + '</div>';
    }).join('') + '</div>';
  }
  /* 原型/05 L3728 · 09 L3964 */
  function bxSec(title, body, mini) {
    return '<div class="bx-sec"><div class="h">' + title + (mini ? '<span class="n">' + mini + '</span>' : '') + '</div>' + body + '</div>';
  }
  /* 原型/05 L3758 · 09 L3994 */
  function why(){
    bxOpen({
      t: '这一单的依据链', icon: ICON, wide: true,
      body: bxChain([
        { t:'会话单', d:'SH-20261021-118 · 李×× · 定期存款到期转存（三年期）',
          b:'单子只记「办什么」，不记为什么能办。' },
        { t:'身份核验', d:'读卡取得证件 · 人证一致',
          b:'读卡已经拿到，<b>不需要客户再手填</b>。' },
        { t:'存单', d:'已核验在本人名下 · 状态正常 · 今日到期',
          b:'存单是「这笔钱是谁的」唯一凭据，缺它就没法证明转的是本人钱。' },
        { t:'本人授权', d:'<span class="warn">待确认</span> · 当面确认 ＋ 录音录像',
          b:'这一环还缺着 —— 所以现在<b>不能出单</b>。', on:true },
        { t:'适当性告知', d:'已提示：利率以办理时挂牌价为准',
          b:'告知不是让客户签个字，是让他知道利率会变。' }
      ]) +
      '<div class="bx-note">链上断在「授权」这一环，窗口就停在这一环 —— <b>不让人跳过断点直接出单</b>，' +
      '是这条链唯一有用的地方。</div>',
      foot: [{ k:'cancel', t:'关闭' }]
    });
  }

  var SLOTS = ['renderClear', 'renderConfirm', 'renderDead', 'renderHall', 'renderQueue', 'renderAppt', 'renderTablet', 'openDrill', 'why', 'bxChain', 'bxSec', 'bxRows'];
  var NAMES = {
    renderClear: '业绩清分', renderConfirm: '网点确认', renderDead: '死账',
    renderHall: '厅堂窗口', renderQueue: '等候队列', renderAppt: '今日预约', renderTablet: '平板',
    openDrill: 'KPI明细', why: '依据链', bxChain: '依据链块', bxSec: '说明段', bxRows: '明细表'
  };

  function mount() {
    if ($('v10ViewBar')) return;
    var board = $('v10Board');
    if (!board || !board.parentNode) return;
    var bar = document.createElement('div');
    bar.id = 'v10ViewBar';
    bar.innerHTML = '<button type="button" data-view="perf">' + entryName() + '</button>' +
      '<button type="button" data-view="hall">现场</button>' +
      '<button type="button" data-view="board">办理表</button>';
    var drawer = document.createElement('div');
    drawer.id = 'v10Drawer';
    drawer.hidden = true;
    var view = document.createElement('div');
    view.id = 'v10View';
    view.hidden = true;
    view.innerHTML = '<div id="v10Perf"><p id="pfLead"></p><div id="pfClearK"></div><div id="pfClearCnt"></div><div id="pfClearList"></div><p id="pfClearNote"></p>' +
      '<p id="pfConfirmLead"></p><div id="pfConfirmList"></div><p id="pfConfirmNote"></p><span id="pfAllN"></span><button type="button" id="pfAll" hidden></button><span id="pfBadge"></span>' +
      '<p id="pfMeetHead"></p><div id="pfMeetBody"></div><div id="pfMeetPool"></div><p id="pfMeetAct"></p><div id="pfMeetSum"></div>' +
      '<div id="pfDeadBar"></div><div id="pfDeadK"></div><div id="pfDeadList"></div><p id="pfDeadNote"></p><span id="pfDeadBadge"></span><span id="pfDeadTab"></span></div>' +
      '<div id="v10Hall" hidden><div data-part="win"><h4>窗口</h4><div id="winGrid"></div><div id="kioskGrid"></div></div><div data-part="queue"><h4>等候</h4><div id="queueList"></div></div><div data-part="appt"><h4>预约</h4><div id="apptList"></div></div><div data-part="tab"><h4>平板</h4><div id="tabActs"></div><div id="tabNote"></div></div></div>' +
      '<div id="v10Built"></div>';
    board.parentNode.insertBefore(bar, board);
    board.parentNode.insertBefore(drawer, board);
    board.parentNode.insertBefore(view, board.nextSibling);
    paintEntry();
    if (!$('drModal')) {
      var mask = document.createElement('div');
      mask.className = 'dr-mask'; mask.id = 'drMask';
      var modal = document.createElement('div');
      modal.className = 'dr-modal'; modal.id = 'drModal'; modal.setAttribute('aria-hidden', 'true');
      modal.innerHTML = '<div class="dr-h"><svg class="ic-xs" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><use id="drIconUse" href="#g-phone"/></svg><b id="drTitle"></b><span class="sp"></span><span class="mini" id="drSub"></span></div><div class="dr-b" id="drBody"></div><div class="dr-f"><button type="button" id="drGoto">去办理</button><button type="button" class="pri" id="drClose">关闭</button></div>';
      document.body.appendChild(mask);
      document.body.appendChild(modal);
      $('drClose').onclick = closeDrill;
      mask.onclick = closeDrill;
    }
    if (!document.getElementById('hallViewCss')) {
      var css = document.createElement('style');
      css.id = 'hallViewCss';
      css.textContent = '#v10ViewBar{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}#v10ViewBar button{height:32px;padding:0 12px;border-radius:8px;border:1px solid #d5ddd8;background:#fff;font-size:13px}#v10ViewBar button.on{background:#e7f3ec;border-color:#9dccb4}#v10Drawer{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:0 0 8px 14px;padding:4px 0 4px 10px;border-left:2px solid #9dccb4}#v10Drawer[hidden]{display:none}#v10Drawer .cap{font-size:12px;color:#5d6a64;margin-right:4px}#v10Drawer button{height:26px;padding:0 10px;border-radius:6px;border:1px solid #e3ebe6;background:#f7faf8;font-size:12px}#v10Drawer button.on{background:#e7f3ec;border-color:#9dccb4}#v10Hall h4{margin:12px 0 6px;font-size:13px;font-weight:600}#v10View{background:#fff;border:1px solid #e3ebe6;border-radius:12px;padding:12px;margin-bottom:12px}#v10View table{width:100%;border-collapse:collapse;font-size:13px}#v10View th,#v10View td{border-bottom:1px solid #eef2ef;padding:6px 8px;text-align:left}.kpi[data-drill]{cursor:pointer} .dr-mask{position:fixed;inset:0;background:rgba(16,24,20,.42);display:none;z-index:80} .dr-mask.on{display:block} .dr-modal{position:fixed;left:50%;top:50%;transform:translate(-50%,-50%);width:min(800px,93vw); max-height:84vh;display:none;flex-direction:column;background:#fff;border-radius:14px; box-shadow:0 26px 64px rgba(10,22,16,.30);z-index:81;overflow:hidden; font-family:inherit;color:var(--t1);text-align:left;padding:0} .dr-modal.on{display:flex} .dr-modal .dr-h{display:flex;align-items:center;gap:9px;padding:14px 18px;border-bottom:1px solid var(--bd-s)} .dr-modal .dr-h .ic-xs{width:14px;height:14px;color:var(--pg);flex:none} .dr-modal .dr-h b{font-size:14.5px;font-weight:600} .dr-modal .dr-h .sp{flex:1} .dr-modal .dr-h .mini{font-size:11.5px;color:var(--t3)} .dr-modal .dr-b{overflow:auto;padding:0 0 8px} .dr-modal .dr-f{display:flex;justify-content:flex-end;gap:9px;padding:11px 18px;border-top:1px solid var(--bd-s);background:#fafcfb} .dr-modal .dr-f button{padding:7px 15px;border-radius:9px;border:1px solid var(--bd-s);background:#fff;font-size:12.5px;cursor:pointer;color:var(--t2);font-family:inherit} .dr-modal .dr-f button.pri{background:var(--pg);border-color:var(--pg);color:#fff} .dr-modal .dr-k{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:14px 18px 4px} .dr-modal .dr-k .box{border:1px solid var(--bd-s);border-radius:10px;padding:10px 13px;background:#fdfefe} .dr-modal .dr-k .box .t{font-size:11.5px;color:var(--t3)} .dr-modal .dr-k .box .v{font-size:19px;color:var(--pg-d);margin-top:4px} .dr-modal .dr-k .box .v u{font-size:11.5px;text-decoration:none;color:var(--t3);margin-left:3px} .dr-modal table{width:100%;border-collapse:collapse;font-size:12.5px} .dr-modal th{background:#f6f9f7;color:var(--t3);font-weight:500;text-align:left;padding:9px 10px;border-bottom:1px solid var(--bd-s);position:sticky;top:0;z-index:1} .dr-modal td{padding:10px;border-bottom:1px solid var(--bd-s);vertical-align:top} .dr-modal tr:last-child td{border-bottom:0} .dr-modal .mono{font-variant-numeric:tabular-nums} .dr-modal .dim{color:var(--t3);font-size:11.5px} .dr-modal .dr-st{display:inline-block;padding:1px 8px;border-radius:20px;font-size:11px;white-space:nowrap} .dr-modal .dr-st-ok{background:#e8f4ee;color:#1f7a4d} .dr-modal .dr-st-wait{background:#fdf2e4;color:#b8621b} .dr-modal .dr-lead{padding:11px 18px 2px;font-size:12px;color:#5d6a64;line-height:1.75} .dr-modal .dr-lead b{color:#1d2a25} .dr-modal .dr-note{padding:10px 18px 6px;font-size:11.5px;color:var(--t3);line-height:1.7} .dr-modal .dr-empty{padding:30px 18px;text-align:center;color:var(--t3);font-size:12.5px}.bx-mk{display:none;position:fixed;inset:0;background:rgba(10,26,18,.35);z-index:82}.bx-mk.on{display:flex;align-items:flex-start;justify-content:center;padding-top:10vh}.bx-dlg{background:#fff;border-radius:14px;width:min(640px,92vw);padding:14px}#pfMeetPool{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}#pfMeetPool button{min-width:72px;padding:8px;border:1px solid #d5ddd8;border-radius:8px;background:#fff}#pfMeetPool button.on{outline:2px solid #1f7a4d}#pfMeetPool button.mt-ok{background:#e5f6ea;border:2px solid #1f8a4c}#pfMeetPool button.mt-proxy{background:#fff4e0;border:2px dashed #e07a00}#pfMeetPool button.mt-wait{background:#fff;border:2px dotted #5d6a64}#pfMeetPool button.mt-absent{background:#fde8e8;border:2px solid #b42318;color:#8a1c14}.mt-self{flex-basis:100%;color:#5d6a64;margin-top:6px}.meet-why{color:#8a1c14;font-weight:600}.till-err{color:#b42318;font-weight:600}';
      document.head.appendChild(css);
    }
  }

  var OPENING_FUND = 100000;
  var MAIL = [
    { k: '普邮', n: 21 }, { k: '特快', n: 18 }, { k: '国际', n: 9 },
    { k: '报刊', n: 6 }, { k: '集邮', n: 3 }, { k: '电商', n: 6 }
  ];
  var MAIL_DRAFT = [{ no: 'SJ-20261020-064' }];
  var AGENCY = [
    { st: '已回传' }, { st: '已回传' }, { st: '已回传' }, { st: '已回传' },
    { st: '已回传' }, { st: '已回传' }, { st: '已回传' }, { st: '已回传' },
    { st: '待回传' }
  ];
  var SLIPS = { take: 69, printed: 56, voided: 1, reprint: 2 };
  var CASH_IN = null;
  var CASH_OUT = null;
  var AUTO_APPROVE = true;
  var TILL = { count: null, hand: null, review: null, close: null, hint: {} };
  var POST_N = {
    P1: { dead: 2, win: 2, queue: 4, appt: 3 },
    P2: { dead: 1, win: 1, queue: 2, appt: 2 },
    P3: { dead: 2, win: 2, queue: 3, appt: 1 },
    P4: { dead: 3, win: 3, queue: 5, appt: 4 },
    P5: { dead: 1, win: 1, queue: 1, appt: 1 }
  };
  var ERR_A = [
    { who: '赵××', obj: '定期开户', n: 1, amt: 12.0, due: '2026-10-20T18:00:00' },
    { who: '钱××', obj: '定期转存', n: 1, amt: 18.5, due: '2026-10-20T18:00:00' },
    { who: '秦××', obj: '收寄批量', n: 1, amt: null, due: '2026-10-20T18:00:00' }
  ];
  var ERR_B = [{ who: '赵××', obj: '缺家庭住址', n: 2, due: '' }];
  var HALL_ARRIVE = [{ k: '已办结', n: 79 }, { k: '办理中', n: 8 }, { k: '待办理', n: 4 }];
  var WAIT_HOURS = [8.2, 7.6, 7.2, 5.4, 6.1, 4.8];
  var FLOW = [{ k: '一次到位', n: 25 }, { k: '转台席', n: 4 }];
  var HALL_TASK = [{ st: '待办理' }, { st: '待办理' }, { st: '待办理' }, { st: '已办结' }, { st: '已办结' }];
  var HALL_CASES = [];
  (function () {
    var i;
    for (i = 0; i < 36; i++) HALL_CASES.push({ st: '一次办成' });
    for (i = 0; i < 3; i++) HALL_CASES.push({ st: '转人工' });
    HALL_CASES.push({ st: '未办结' });
  })();
  var DATA = {
    staff: { src: 'local', rows: STAFF },
    day: { src: 'api', value: DAY },
    counts: { src: 'local', rows: POST_N },
    perf: { src: 'local', rows: BASE },
    mail: { src: 'local', rows: MAIL },
    draft: { src: 'local', rows: MAIL_DRAFT },
    agency: { src: 'local', rows: AGENCY },
    slips: { src: 'local', rows: SLIPS },
    cashIn: { src: 'none', value: CASH_IN },
    cashOut: { src: 'none', value: CASH_OUT },
    err: { src: 'local', rows: ERR_A.concat(ERR_B) },
    hall: { src: 'local', rows: { arrive: HALL_ARRIVE, wait: WAIT_HOURS, flow: FLOW, task: HALL_TASK, cases: HALL_CASES } },
    drill: { src: 'local', rows: null }
  };

  function sumN(list, key) {
    var s = 0;
    list.forEach(function (r) { s += Number(r[key]) || 0; });
    return s;
  }
  function hm() {
    var d = new Date();
    return (d.getHours() < 10 ? '0' : '') + d.getHours() + ':' + (d.getMinutes() < 10 ? '0' : '') + d.getMinutes();
  }
  function moneyIn(raw) {
    var s = String(raw == null ? '' : raw).trim();
    if (s === '') return { err: '请填数字' };
    var n = Number(s);
    if (isNaN(n)) return { err: '不是数字' };
    if (n < 0) return { err: '不能为负' };
    return { n: n };
  }
  function money2(n) {
    return Number(n).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function dueState(iso) {
    var end = new Date(iso).getTime();
    var diff = Date.now() - end;
    if (diff < 0) return '待补录 · 剩 ' + Math.ceil(-diff / 3600000) + ' 小时';
    var days = Math.floor(diff / 86400000);
    var hours = Math.floor((diff % 86400000) / 3600000);
    return '已逾期 ' + days + ' 天 ' + hours + ' 小时 · 转差错';
  }
  function todayClose() {
    var d = new Date();
    var m = d.getMonth() + 1;
    var day = d.getDate();
    return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day + 'T18:00:00';
  }
  function slipLeft() { return SLIPS.take - SLIPS.printed - SLIPS.voided; }
  function shouldKeep() {
    if (CASH_IN == null || CASH_OUT == null) return null;
    return OPENING_FUND + sumN(CASH_IN, 'a') - sumN(CASH_OUT, 'a');
  }

  function renderErr() {
    var bDue = todayClose();
    var rows = ERR_A.map(function (r) {
      return [r.who, r.obj, r.n + ' 笔', r.amt == null ? '—' : r.amt + ' 万', '10-20 18:00', dueState(r.due), '补录'];
    }).concat(ERR_B.map(function (r) {
      return [r.who, r.obj, r.n + ' 户', '—', '今日日终', dueState(bDue), '补家庭住址'];
    }));
    var head = ['责任人', '对象', '数量', '金额', '截止', '状态', '动作'];
    $('v10Built').innerHTML = '<p>补录 / 缺项。A 类 ' + ERR_A.length + ' 笔未补录，B 类 ' +
      sumN(ERR_B, 'n') + ' 户缺项。</p><table><tr>' +
      head.map(function (h) { return '<th>' + h + '</th>'; }).join('') + '</tr>' +
      rows.map(function (r) {
        return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
      }).join('') + '</table>';
  }

  function renderSettle() {
    var pieces = sumN(MAIL, 'n');
    var back = AGENCY.filter(function (a) { return a.st === '已回传'; }).length;
    var keep = shouldKeep();
    var keepTxt = keep == null ? '应存未定' : money2(keep);
    var lines = [
      ['收寄件数', pieces + ' 件', MAIL.map(function (m) { return m.k + ' ' + m.n; }).join(' ＋ ')],
      ['未提交草稿', MAIL_DRAFT.length + ' 单', MAIL_DRAFT.map(function (d) { return d.no; }).join('、')],
      ['代办回传', back + ' / ' + AGENCY.length + ' 笔', '代办不占收寄件数'],
      ['空白凭证', slipLeft() + ' 张', '领用 ' + SLIPS.take + ' − 已打 ' + SLIPS.printed + ' − 作废 ' + SLIPS.voided + '（补打 ' + SLIPS.reprint + ' 张不占新凭证）'],
      ['现金尾箱', '领 → 用 → 点 → 交', '点库、上交两道都过，并且应存已知，才能结账']
    ];
    var counted = TILL.count && TILL.count.at;
    var handed = TILL.hand && TILL.hand.at;
    var sealed = !!TILL.close;
    var diff = (counted && keep != null) ? (Number(TILL.count.real) - keep) : null;
    var diffTxt = keep == null ? '应存未定 · 差额算不出'
      : (diff == null ? '' : (Math.abs(diff) < 0.005 ? '点库平' : (diff < 0 ? '短款 ¥' + money2(-diff) : '长款 ¥' + money2(diff))));
    var hint = function (k) { return TILL.hint[k] ? ' <span class="till-err">' + TILL.hint[k] + '</span>' : ''; };
    var countCell = counted
      ? (nameOf(TILL.count.by) + '（' + TILL.count.by + '）· ' + TILL.count.at + ' · 实存 ' + money2(TILL.count.real) + ' · ' + diffTxt + (sealed ? '' : ' <button type="button" data-act="redoCount">重记</button>'))
      : '未点库 <input id="tillReal" inputmode="decimal" placeholder="实存"> <button type="button" id="tillCount">点库</button>' + hint('count');
    var bal = (counted && handed) ? (Number(TILL.count.real) - Number(TILL.hand.amount)) : null;
    var balTxt = bal == null ? '' : (Math.abs(bal) < 0.005 ? ' · 已交清' : (bal > 0 ? ' · 未交清 ¥' + money2(bal) : ' · 多交 ¥' + money2(-bal)));
    var handCell = handed
      ? (nameOf(TILL.hand.by) + '（' + TILL.hand.by + '）· ' + TILL.hand.at + ' · 上交 ' + money2(TILL.hand.amount) + balTxt + (sealed ? '' : ' <button type="button" data-act="redoHand">重记</button>'))
      : '未上交 <input id="tillAmt" inputmode="decimal" placeholder="上交金额"> <button type="button" id="tillHand">上交</button>' + hint('hand');
    var reviewCell = (AUTO_APPROVE && TILL.review)
      ? ('复核人：' + TILL.review.by + ' · 自动通过 · 未签认 · ' + TILL.review.at)
      : '未复核 <button type="button" id="tillReview">复核</button>';
    var gates = keep != null && counted && handed && diff != null && bal != null && Math.abs(diff) < 0.005 && Math.abs(bal) < 0.005;
    var closeDis = (sealed || !gates) ? ' disabled' : '';
    var closeWhy = sealed ? '' : (keep == null ? '应存未定 · 差额算不出' : '');
    var closeLine = sealed
      ? '<tr><td>已结账</td><td>已结账 · ' + TILL.close.at + ' · ' + nameOf(TILL.close.by) + '（' + TILL.close.by + '）· 自动通过 · 未签认</td></tr>' +
        '<tr><td>明日期初</td><td>明日期初运营金按今日上报数 ' + money2(TILL.close.should) + ' 拨付</td></tr>'
      : '';
    var inCell = sealed || CASH_IN != null
      ? money2(sumN(CASH_IN, 'a'))
      : '未定 <input id="cashIn" inputmode="decimal" placeholder="当日现金收入"> <button type="button" id="cashInGo">记收入</button>' + hint('in');
    var outCell = sealed || CASH_OUT != null
      ? money2(sumN(CASH_OUT, 'a'))
      : '未定 <input id="cashOut" inputmode="decimal" placeholder="当日现金支出"> <button type="button" id="cashOutGo">记支出</button>' + hint('out');
    var till = '<table><tr><th>段</th><th>状态</th></tr>' +
      '<tr><td>领 · 期初运营金</td><td>' + money2(OPENING_FUND) + '（未申报 · 默认档）</td></tr>' +
      '<tr><td>用 · 当日现金收入</td><td>' + inCell + '</td></tr>' +
      '<tr><td>用 · 当日现金支出</td><td>' + outCell + '</td></tr>' +
      '<tr><td>应存</td><td>' + keepTxt + '</td></tr>' +
      '<tr><td>点 · 点库</td><td>' + countCell + '</td></tr>' +
      '<tr><td>交 · 上交</td><td>' + handCell + '</td></tr>' +
      '<tr><td>双人复核</td><td>' + reviewCell + '</td></tr>' + closeLine + '</table>' +
      '<p><button type="button" id="tillClose"' + closeDis + '>' + (sealed ? '本日账已封' : '结账') + '</button> ' + closeWhy + '</p>' +
      '<p>数据源：收寄/凭证/代办/差错 来自本地兜底（接口未接入）· 名册来自' +
      (DATA.staff.src === 'api' ? '后端已接入' : '本地兜底') + '</p>';
    $('v10Built').innerHTML = '<p>检查项 ' + lines.length + ' 项。收寄 ' + pieces + ' 件。</p><table><tr><th>检查项</th><th>数</th><th>怎么来的</th></tr>' +
      lines.map(function (r) {
        return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
      }).join('') + '</table>' + till;
    var c = $('tillCount');
    if (c) c.onclick = function () {
      var got = moneyIn($('tillReal') && $('tillReal').value);
      if (got.err) { TILL.hint.count = got.err; renderSettle(); return; }
      TILL.hint.count = '';
      var prev = TILL.count && TILL.count.prev;
      TILL.count = { at: hm(), by: meNo(), real: got.n, diff: (shouldKeep() == null ? null : got.n - shouldKeep()), prev: prev || null };
      renderSettle();
    };
    var h = $('tillHand');
    if (h) h.onclick = function () {
      var got = moneyIn($('tillAmt') && $('tillAmt').value);
      if (got.err) { TILL.hint.hand = got.err; renderSettle(); return; }
      TILL.hint.hand = '';
      var prev = TILL.hand && TILL.hand.prev;
      TILL.hand = { at: hm(), by: meNo(), amount: got.n, prev: prev || null };
      renderSettle();
    };
    var inn = $('cashInGo');
    if (inn) inn.onclick = function () {
      var got = moneyIn($('cashIn') && $('cashIn').value);
      if (got.err) { TILL.hint['in'] = got.err; renderSettle(); return; }
      TILL.hint['in'] = '';
      CASH_IN = [{ a: got.n }];
      renderSettle();
    };
    var out = $('cashOutGo');
    if (out) out.onclick = function () {
      var got = moneyIn($('cashOut') && $('cashOut').value);
      if (got.err) { TILL.hint.out = got.err; renderSettle(); return; }
      TILL.hint.out = '';
      CASH_OUT = [{ a: got.n }];
      renderSettle();
    };
    var v = $('tillReview');
    if (v) v.onclick = function () {
      TILL.review = { at: hm(), by: '综合柜员', signed: false, mode: AUTO_APPROVE ? 'auto' : 'manual' };
      renderSettle();
    };
  }

  function renderHallStat() {
    var arrive = sumN(HALL_ARRIVE, 'n');
    var wait = 0;
    WAIT_HOURS.forEach(function (n) { wait += n; });
    wait = (wait / WAIT_HOURS.length);
    var apptIn = DR_APPTS.filter(function (a) { return a.st === '今日到店'; }).length;
    var apptRate = Math.round(apptIn / DR_APPTS.length * 100);
    var flowOk = FLOW.filter(function (f) { return f.k === '一次到位'; })[0].n;
    var flowN = sumN(FLOW, 'n');
    var flowRate = Math.round(flowOk / flowN * 100);
    var taskOk = HALL_TASK.filter(function (t) { return t.st === '已办结'; }).length;
    var done = HALL_CASES.filter(function (c) { return c.st === '一次办成'; }).length;
    var doneRate = Math.round(done / HALL_CASES.length * 100);
    var rows = [
      ['到访', arrive + ' 人', HALL_ARRIVE.map(function (a) { return a.k + ' ' + a.n; }).join(' ＋ ')],
      ['平均等候', wait.toFixed(1) + ' 分', '六个时段平均，不与人数相加'],
      ['预约到店率', apptRate + '%', apptIn + ' / ' + DR_APPTS.length],
      ['分流成功率', flowRate + '%', flowOk + ' / ' + flowN],
      ['待办', taskOk + '/' + HALL_TASK.length, '已办结 / 全部'],
      ['回访', DR_VISITS.length + ' 户', '回访记录条数'],
      ['预约', DR_APPTS.length + ' 笔', '预约记录条数'],
      ['办成率', doneRate + '%', done + ' / ' + HALL_CASES.length + ' · 厅堂口径']
    ];
    $('v10Built').innerHTML = '<p>到访 ' + arrive + ' 人。八个指标分行，人数、时长、比例不相加。</p><table><tr><th>指标</th><th>数</th><th>口径</th></tr>' +
      rows.map(function (r) {
        return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>';
      }).join('') + '</table>';
  }

  var MEET_I = 0;
  var MEET_FOR = '';
  var MEET_SUM = '';
  var REJ_I = -1;
  function proxyOf(r, no) {
    return (r.proxy || []).filter(function (p) { return p.forNo === no; })[0];
  }
  function renderMeet() {
    var list = PERF;
    if (!list.length) { $('pfMeetBody').textContent = '今天没有笔。'; return; }
    if (MEET_I < 0) MEET_I = 0;
    if (MEET_I >= list.length) MEET_I = list.length - 1;
    var r = list[MEET_I];
    var pool = VOTERS.filter(function (n) { return n !== byOf(r); });
    $('pfMeetHead').textContent = '清分会议　第 ' + (MEET_I + 1) + ' / ' + list.length + ' 笔';
    var absHere = r.absent || [];
    $('pfMeetBody').innerHTML = r.t + '　' + r.k + '　' + f1(r.a) + (r.u === 'piece' ? ' 件' : ' 万元') + '　1 笔<br>经办：' +
      nameOf(byOf(r)) + '（' + byOf(r) + '）· ' + (r.src || '') + '录入 · 状态：' + ST[stOf(r)][0] +
      '<br>票池　' + VOTERS.length + ' 人可投 · 扣经办人自己后 ' + pool.length + ' 票 · 现 ' + votesOf(r).length + ' 票' +
      (absHere.length ? '<br>缺席 ' + absHere.length + ' 人 · ' + absHere.map(function (a) { return nameOf(a.no); }).join('、') : '') +
      (r.draft ? '<br>这一笔是草稿，本人还没核对，任何人不能替投' : '');
    $('pfMeetPool').innerHTML = pool.map(function (n) {
      var prox = proxyOf(r, n);
      var voted = votesOf(r).indexOf(n) >= 0;
      var gone = absHere.some(function (a) { return a.no === n; });
      var cls = prox ? 'mt-proxy' : (gone ? 'mt-absent' : (voted ? 'mt-ok' : 'mt-wait'));
      var txt = prox ? '已投 · 代 △' : (gone ? '缺席 ×' : (voted ? '已投 ✓' : '未投 ○'));
      return '<button type="button" class="' + cls + (MEET_FOR === n ? ' on' : '') + '" data-act="meetPick" data-no="' + n + '"' +
        (prox ? " data-proxy='" + JSON.stringify(prox).replace(/'/g, '') + "'" : '') + '>' +
        nameOf(n) + '<br>' + txt + '</button>';
    }).join('') + '<div class="mt-self">' + nameOf(byOf(r)) + '（' + byOf(r) + '）经办人 · 不自投</div>';
    var absRec = MEET_FOR ? absHere.filter(function (a) { return a.no === MEET_FOR; })[0] : null;
    var votedP = !!(MEET_FOR && votesOf(r).indexOf(MEET_FOR) >= 0);
    var why = '';
    if (MEET_FOR && r.draft) why = '这一笔是草稿，本人还没核对，任何人不能替投';
    else if (votedP) why = '已投，不能记缺席';
    else if (absRec) why = '已记缺席 · ' + nameOf(absRec.byNo) + '（' + absRec.byNo + '）· ' + absRec.at;
    var can = MEET_FOR && MEET_FOR !== byOf(r) && !votedP && !absRec && !r.draft;
    $('pfMeetAct').innerHTML =
      '<button type="button" data-act="meetProxy"' + (can ? '' : ' disabled') + '>代记通过' + (MEET_FOR ? ' · ' + nameOf(MEET_FOR) : '') + '</button> ' +
      '<button type="button" data-act="meetAbsent"' + (can ? '' : ' disabled') + '>记缺席</button> ' +
      (why ? '<span class="meet-why">' + why + '</span> ' : '') +
      '<button type="button" data-act="meetRej">驳回</button> ' +
      '<button type="button" data-act="meetPrev">上一笔</button> ' +
      '<button type="button" data-act="meetNext">下一笔</button> ' +
      '<button type="button" data-act="meetEnd">结束清分 · 剩 ' +
        PERF.filter(function (x) { return stOf(x) === 'wait'; }).length + ' 笔未投齐 · ' +
        PERF.filter(function (x) { return !!x.draft; }).length + ' 笔待核对</button>';
    $('pfMeetSum').innerHTML = MEET_SUM;
  }
  function meetSummary() {
    var proxRows = 0, proxN = 0, selfOk = 0, waitN = 0, draftN = 0, lines = [], abs = {}, unvoted = 0;
    PERF.forEach(function (r) {
      var px = r.proxy || [];
      if (px.length) {
        proxRows++;
        proxN += px.length;
        lines.push(r.t + ' ' + r.k + ' ' + f1(r.a) + ' —— ' + px.map(function (p) { return nameOf(p.forNo) + '（' + p.forNo + '）'; }).join('、'));
      } else if (stOf(r) === 'ok') selfOk++;
      if (stOf(r) === 'wait') waitN++;
      if (r.draft) draftN++;
      (r.absent || []).forEach(function (a) { abs[a.no] = nameOf(a.no); });
      unvoted += pendingOf(r).length;
    });
    var absNames = Object.keys(abs).map(function (n) { return abs[n]; });
    var line = '本次清分 ' + PERF.length + ' 笔：本人投齐 ' + selfOk + ' 笔 · 会上代记 ' + proxRows + ' 笔（共 ' + proxN + ' 张票，均未签认）' +
      ' · 未投齐 ' + waitN + ' 笔（退死账，明日挂支局长待办）· 待本人核对 ' + draftN + ' 笔（不退，本人核对后重新计票）' +
      '<br>缺席 ' + absNames.length + ' 人' + (absNames.length ? '（' + absNames.join('、') + '）' : '') + ' · 未投 ' + unvoted + ' 人';
    return line + (lines.length ? '<br>代记明细：' + lines.join('；') : '');
  }

  function entryName() {
    return { P1: '业绩清分', P2: '我的业绩', P3: '我的业绩', P4: '厅堂统计' }[ROLE] || '业绩';
  }
  function drawerSpec() {
    if (ROLE === 'P1') return [['renderClear', '每日清分'], ['renderConfirm', '网点确认'], ['renderDead', '死账'], ['renderMeet', '清分会议']];
    if (ROLE === 'P2') return [['renderClear', '我的业绩'], ['renderConfirm', '网点确认'], ['renderErr', '差错复核']];
    if (ROLE === 'P3') return [['renderSettle', '日终结算'], ['renderClear', '我的业绩'], ['renderConfirm', '网点确认']];
    if (ROLE === 'P4') return [['renderHallStat', '厅堂统计'], ['renderQueue', '等候时长'], ['renderClear', '业绩清分'], ['renderConfirm', '网点确认']];
    return [['renderClear', '每日清分'], ['renderConfirm', '网点确认'], ['renderDead', '死账']];
  }
  function paintEntry() {
    var b = document.querySelector('#v10ViewBar button[data-view="perf"]');
    if (b) b.textContent = entryName();
    var d = $('v10Drawer');
    if (!d) return;
    var spec = drawerSpec();
    d.innerHTML = spec.map(function (x) {
        return '<button type="button" data-view="' + x[0] + '">' + x[1] + '</button>';
      }).join('');
  }
  function markNav(name) {
    var drawer = $('v10Drawer');
    var inDrawer = drawer && drawer.querySelector('button[data-view="' + name + '"]');
    var perf = name === 'perf' || !!inDrawer;
    if (drawer) drawer.hidden = !perf;
    Array.prototype.forEach.call(document.querySelectorAll('#v10ViewBar button, #v10Drawer button'), function (b) {
      var v = b.getAttribute('data-view');
      var on = v === name || (perf && v === 'perf') || (name === 'hall' && v === 'hall');
      b.classList.toggle('on', on);
    });
  }
  function showBoard() {
    mount();
    var view = $('v10View');
    var board = $('v10Board');
    if (view) view.hidden = true;
    if (board) board.hidden = false;
    markNav('board');
  }

  function show(name) {
    mount();
    if (name === 'perf') name = drawerSpec()[0][0];
    var view = $('v10View');
    var board = $('v10Board');
    if (name === 'board') { showBoard(); return; }
    if (board) board.hidden = true;
    if (view) view.hidden = false;
    ['pfLead', 'pfClearK', 'pfClearCnt', 'pfClearList', 'pfClearNote', 'pfConfirmLead', 'pfConfirmList', 'pfConfirmNote', 'pfDeadBar', 'pfDeadK', 'pfDeadList', 'pfDeadNote', 'pfMeetHead', 'pfMeetBody', 'pfMeetPool', 'pfMeetAct', 'pfMeetSum', 'winGrid', 'kioskGrid', 'queueList', 'apptList', 'tabActs', 'tabNote', 'v10Built'].forEach(function (id) {
      var n = $(id); if (n) n.innerHTML = '';
    });
    var perfBox = $('v10Perf');
    var hallBox = $('v10Hall');
    var floor = name === 'hall' || name === 'renderQueue';
    var built = name === 'renderErr' || name === 'renderSettle' || name === 'renderHallStat';
    if (perfBox) perfBox.hidden = floor || built;
    if (hallBox) {
      hallBox.hidden = !floor;
      Array.prototype.forEach.call(hallBox.querySelectorAll('[data-part]'), function (p) {
        p.hidden = name === 'renderQueue' && p.getAttribute('data-part') !== 'queue';
      });
    }
    if (name === 'renderClear') renderClear();
    else if (name === 'renderConfirm') renderConfirm();
    else if (name === 'renderDead') renderDead();
    else if (name === 'renderErr') renderErr();
    else if (name === 'renderSettle') renderSettle();
    else if (name === 'renderHallStat') renderHallStat();
    else if (name === 'renderMeet') renderMeet();
    else if (name === 'renderQueue') renderQueue();
    else if (name === 'hall') {
      renderHall();
      renderQueue();
      renderAppt();
      renderTablet();
    }
    markNav(name);
  }

  function drillKind(s) {
    if (/到店率/.test(s)) return 'apptRate';
    if (/分流/.test(s)) return 'flow';
    if (/等候/.test(s)) return DRILL.wait ? 'wait' : 'arrive';
    if (/流失/.test(s)) return 'saveOut';
    if (/新增|新进|储蓄进/.test(s)) return 'saveIn';
    if (/办成/.test(s)) return 'rate';
    if (/待办/.test(s)) return 'task';
    if (/办理|笔数/.test(s)) return 'biz';
    if (/到访|进店/.test(s)) return 'arrive';
    if (/预约/.test(s)) return 'appt';
    if (/回访/.test(s)) return 'visit';
    return '';
  }
  function consume(label) {
    var s = String(label || '');
    var name = '';
    if (/清分会议/.test(s)) name = 'renderMeet';
    else if (/死账/.test(s)) name = 'renderDead';
    else if (/确认/.test(s)) name = 'renderConfirm';
    else if (/清分|业绩/.test(s)) name = 'renderClear';
    else if (/队列|叫号|预约|厅堂|窗口|平板/.test(s)) name = 'hall';
    if (name) { show(name); return; }
    var kind = drillKind(s);
    if (kind && DRILL[kind]) { openDrill(kind); return; }
    DRILL._hit = { title: s || '明细', sub: '', icon: 'g-doc', cols: [], rows: [], note: '' };
    openDrill('_hit');
  }

  document.addEventListener('click', function (e) {
    var d = e.target && e.target.closest ? e.target.closest('[data-drill]') : null;
    if (d) { openDrill(d.getAttribute('data-drill')); return; }
    var meet = e.target && e.target.closest ? e.target.closest('[data-act^="meet"]') : null;
    if (meet) {
      var act = meet.getAttribute('data-act');
      var row = PERF[MEET_I];
      if (act === 'meetPick') MEET_FOR = meet.getAttribute('data-no');
      else if (act === 'meetPrev') MEET_I -= 1;
      else if (act === 'meetNext') MEET_I += 1;
      else if (act === 'meetEnd') MEET_SUM = meetSummary();
      else if (row && act === 'meetProxy' && MEET_FOR && MEET_FOR !== byOf(row) && votesOf(row).indexOf(MEET_FOR) < 0 && !row.draft) {
        votesOf(row).push(MEET_FOR);
        row.proxy = (row.proxy || []).concat([{ forNo: MEET_FOR, byNo: meNo(), at: (function () { var d = new Date(); return (d.getHours() < 10 ? '0' : '') + d.getHours() + ':' + (d.getMinutes() < 10 ? '0' : '') + d.getMinutes(); })(), mode: '会议代记', signed: false }]);
      } else if (row && act === 'meetAbsent' && MEET_FOR && votesOf(row).indexOf(MEET_FOR) < 0 && !(row.absent || []).some(function (a) { return a.no === MEET_FOR; })) {
        row.absent = (row.absent || []).concat([{ no: MEET_FOR, byNo: meNo(), at: hm() }]);
      } else if (row && act === 'meetRej') {
        rejsOf(row).push({ who: meNo(), why: '清分会驳回' });
      }
      renderMeet();
      return;
    }
    var book = e.target && e.target.closest ? e.target.closest('[data-act="okWho"], [data-act="rejOne"], [data-act="rejWhy"], [data-act="redoCount"], [data-act="redoHand"], #tillClose') : null;
    if (book) {
      var kind = book.id === 'tillClose' ? 'tillClose' : book.getAttribute('data-act');
      if (kind === 'okWho') {
        var who = book.getAttribute('data-who');
        PERF.forEach(function (r) {
          if (byOf(r) === who && canVote(r)) votesOf(r).push(meNo());
        });
        renderConfirm();
      } else if (kind === 'rejOne') {
        REJ_I = Number(book.getAttribute('data-i'));
        renderConfirm();
      } else if (kind === 'rejWhy') {
        var rr = PERF[Number(book.getAttribute('data-i'))];
        if (rr) rejsOf(rr).push({ who: meNo(), why: book.getAttribute('data-why'), at: hm() });
        REJ_I = -1;
        renderConfirm();
      } else if (kind === 'redoCount' && TILL.count && TILL.count.at && !TILL.close) {
        TILL.count = { prev: { at: TILL.count.at, by: TILL.count.by, real: TILL.count.real, diff: TILL.count.diff, prev: TILL.count.prev || null } };
      } else if (kind === 'redoHand' && TILL.hand && TILL.hand.at && !TILL.close) {
        TILL.hand = { prev: { at: TILL.hand.at, by: TILL.hand.by, amount: TILL.hand.amount, prev: TILL.hand.prev || null } };
      } else if (kind === 'tillClose' && !book.disabled && !TILL.close) {
        var keepNow = shouldKeep();
        var real = TILL.count && TILL.count.real;
        var hand = TILL.hand && TILL.hand.amount;
        TILL.close = {
          at: hm(), by: meNo(), opening: OPENING_FUND,
          cashIn: CASH_IN == null ? null : sumN(CASH_IN, 'a'),
          cashOut: CASH_OUT == null ? null : sumN(CASH_OUT, 'a'),
          should: keepNow, real: real, hand: hand,
          diff: real - keepNow, bal: real - hand, mode: 'auto'
        };
      }
      if (kind === 'redoCount' || kind === 'redoHand' || kind === 'tillClose') renderSettle();
      return;
    }
    var vote = e.target && e.target.closest ? e.target.closest('[data-act="vote"]') : null;
    if (vote) {
      var row = PERF[Number(vote.getAttribute('data-i'))];
      if (row && canVote(row)) {
        votesOf(row).push(meNo());
        if ($('v10Drawer') && $('v10Drawer').querySelector('button.on[data-view="renderConfirm"]')) renderConfirm();
        else renderClear();
      }
      return;
    }
    var jump = e.target && e.target.closest ? e.target.closest('#quickrow button') : null;
    if (jump) {
      var name = jump.getAttribute('data-jump');
      var id = name === '查看预约' ? 'apptList' : (name === '为客户取号' ? 'queueList' : 'winGrid');
      var node = $(id);
      if (node && node.scrollIntoView) node.scrollIntoView({ block: 'center' });
      return;
    }
    var b = e.target && e.target.closest ? e.target.closest('#v10ViewBar button, #v10Drawer button') : null;
    if (!b) return;
    e.preventDefault();
    show(b.getAttribute('data-view'));
  });

  function proof(name) {
    show(name || 'renderClear');
    var list = scopeRows();
    var table = $('pfClearList');
    var rows = table ? table.querySelectorAll('tr').length - 1 : 0;
    var heads = [];
    if (table) table.querySelectorAll('th').forEach(function (th) { heads.push(th.textContent); });
    return { me: ME, scope: SCOPE, rows: rows, sum: f1(sumOf(list)), heads: heads.join('|') };
  }

  use('P1');
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount);
  else mount();

  function applyStaff(rows) {
    STAFF = rows.map(function (r) {
      var code = toShellRole(r.role_code);
      var gap = !r.role_code;
      var st = r.account_state === 'refuse' ? '拒绝' : '在岗';
      return { no: r.employee_no, name: r.name, role: code, st: st, gap: gap ? '后端无角色' : '' };
    });
    DATA.staff.rows = STAFF;
    DATA.staff.src = 'api';
    rebuildVoters();
    var found = bindMe(SESSION_NO);
    if (!found) ME.missing = true;
    seed();
  }
  function mapCheck() {
    var want = { '1001': 'P1', '1003': 'P2', '1017': 'P3', '1004': 'P4' };
    var out = {};
    Object.keys(want).forEach(function (no) {
      var row = STAFF.filter(function (s) { return s.no === no; })[0];
      out[row ? row.name : no] = row ? row.role : '';
    });
    return out;
  }
  function loadStaff() {
    fetch('/api/staff').then(function (r) { return r.json(); }).then(function (body) {
      if (body && body.staff && body.staff.length) applyStaff(body.staff);
    }).catch(function () {});
  }
  loadStaff();

  window.HallViews = {
    use: use, show: show, consume: consume, proof: proof,
    openDrill: openDrill, renderHall: renderHall, renderQueue: renderQueue, renderAppt: renderAppt,
    renderTablet: renderTablet, renderClear: renderClear, renderDead: renderDead, renderConfirm: renderConfirm,
    why: why, bxChain: bxChain, bxSec: bxSec, bxRows: bxRows,
    DATA: DATA, mapCheck: mapCheck, seed: seed,
    staffName: nameOf, bindMe: bindMe
  };
})();
