/* 二级页目录只写这一处。左栏 pgroup、功能区、hall-keys 都用它。 */
window.PAGE_BASE = '二级页/';

/* 同一岗位的功能区只认这一张表。页面不再各写一份去处。 */
window.HALL_GO = {
  P1: {
    '报表导出': '06_业务报表总览.html',
    '岗位对比': '06_统计.html#岗位对比',
    '待我授权': '06_授权.html#待我授权',
    '授权规则': '06_授权.html#授权规则',
    '岗位名册': '06_员工.html#本局',
    '排班与在岗': '06_排班与在岗.html#今日',
    '调岗与交接': '06_调岗与交接.html#调岗申请',
    '调岗申请': '06_调岗与交接.html#调岗申请',
    '交接单': '06_调岗与交接.html#交接单',
    '授权流水': '06_授权.html#已授权记录',
    '异常预警': '08_审计.html#异常预警',
    '全支局': '06_业务.html#支局业务',
    '逐岗位': '06_员工.html#本局',
    '批量批准': '06_授权.html#待我授权',
    '加急催办': '06_授权.html#待我授权'
  },
  P2: {
    '开户': '05_账户.html#开户',
    '存取': '05_业务.html#储蓄存取',
    '理财': '05_业务.html#理财代销',
    '转人工': '05_统计.html#转人工记录'
  },
  P3: {
    '邮件查询': '07_收寄.html#邮件查询',
    '待封发': '07_收寄.html#待封发',
    '社保': '07_代办.html#社保',
    '交管': '07_代办.html#交管',
    '税邮': '07_代办.html#税邮',
    '票务警邮': '07_代办.html#票务与警邮',
    '报刊订阅': '07_邮务.html#报刊订阅',
    '集邮': '07_邮务.html#集邮',
    '汇兑': '07_邮务.html#汇兑',
    '电商农品': '07_邮务.html#电商与农品',
    '建档': '07_客户.html#开发新客户',
    '预约': '07_客户.html#预约客户',
    '回访': '07_客户.html#待回访',
    '管户': '07_客户.html#重点客户',
    '政务代办': '06_业务.html#政务代办'
  },
  P4: {
    '预约查询': '09_业务.html#预约管理',
    '客户分流': '09_业务.html#客户分流',
    '预约登记': '09_业务.html#预约管理',
    '巡检': '09_业务.html#厅堂巡检',
    '材料预检': '09_业务.html#代办引导',
    '代办引导': '09_业务.html#代办引导',
    '厅堂巡检': '09_业务.html#厅堂巡检',
    '预约管理': '09_业务.html#预约管理'
  },
  P5: {
    '组织架构': '08_组织.html#人员网络',
    '调岗': '08_组织.html#调岗与交接',
    '交接单': '08_组织.html#调岗与交接',
    '权限矩阵': '08_组织.html#权限授予',
    '岗位模板': '08_组织.html#岗位模板',
    '花名册': '08_组织.html#人员网络',
    '权限包': '08_组织.html#权限授予',
    '业务参数': '08_参数.html#业务参数',
    '参数总表': '08_参数.html#业务参数',
    '授权规则': '08_参数.html#授权规则',
    '时限阈值': '08_参数.html#时限阈值',
    '话术模板': '08_参数.html#话术模板',
    '数据目录': '08_数据.html#数据目录',
    '备份': '08_数据.html#备份与归档',
    '密钥托管': '08_数据.html#生命周期',
    '脱敏规则': '08_数据.html#脱敏规则',
    '保留期规则': '08_数据.html#生命周期',
    '处置队列': '08_数据.html#生命周期',
    '销毁凭证': '08_数据.html#生命周期',
    '全局报表': '08_报表.html#全局报表',
    '运营看板': '08_报表.html#运营看板',
    '趋势分析': '08_报表.html#趋势分析',
    '口径对账': '08_报表.html#口径对账',
    '异常预警': '08_审计.html#异常预警',
    '预警处置': '08_审计.html#异常预警',
    '操作留痕': '08_审计.html#操作留痕',
    '留痕检索': '08_审计.html#操作留痕',
    '破玻璃记录': '08_审计.html#破玻璃记录',
    '破玻璃': '08_审计.html#破玻璃记录',
    '合规台账': '08_审计.html#操作留痕',
    '服务状态': '08_系统.html#服务状态',
    '接口与能力': '08_系统.html#接口与能力',
    '模型配置': '08_系统.html#模型配置'
  }
};

/* 每个岗位一份功能区。这个岗位下的每一页都用这一份，不再各页另排一套键。 */
window.HALL_RIBBON = {
  P1: [
    { g:'岗位视图', cls:'g-view', items:[['g-grid','全支局'],['g-users','逐岗位'],['g-chart','报表导出'],['g-eye','岗位对比']] },
    { g:'授权审批', cls:'g-auth', items:[['g-shield','待我授权',1],['g-check','批量批准'],['g-rule','授权规则'],['g-bell','加急催办']] },
    { g:'人员', cls:'g-people', items:[['g-users','岗位名册'],['g-cal','排班与在岗'],['g-transfer','调岗申请'],['g-doc','交接单']] },
    { g:'会话', cls:'g-session', items:[['g-take','接管'],['g-resume','断点续办'],['g-transfer','转派'],['g-plus','新建会话']] },
    { g:'审计留痕', cls:'g-audit', items:[['g-trace','操作留痕'],['g-list','授权流水'],['g-flag','异常预警']] }
  ],
  P2: [
    { g:'接入身份', cls:'g-access', items:[['g-id','读卡'],['g-user','身份证'],['g-cam','人脸核验']] },
    { g:'会话', cls:'g-session', items:[['g-plus','新建会话'],['g-take','接管'],['g-resume','断点续办'],['g-transfer','转人工']] },
    { g:'金融事项', cls:'g-item', items:[['g-home','开户'],['g-coins','存取'],['g-chart','理财'],['g-cam','双录']] },
    { g:'依据核验', cls:'g-evidence', items:[['g-verify','身份核验'],['g-rule','授权与双录'],['g-trace','留痕']] },
    { g:'工具', cls:'g-tool', items:[['g-print','打印凭条'],['g-scan','凭证扫描'],['g-eye','模型观测']] }
  ],
  P3: [
    { g:'收寄', cls:'g-mail', items:[['g-camera','验视'],['g-scale','称重计费',1],['g-print','打印面单'],['g-force','保价'],['g-search','邮件查询']] },
    { g:'代办', cls:'g-agent', items:[['g-gov','社保'],['g-id','交管'],['g-stamp','税邮'],['g-news','票务警邮']] },
    { g:'邮务', cls:'g-post', items:[['g-news','报刊订阅'],['g-stamp','集邮'],['g-money','汇兑'],['g-box','电商农品']] },
    { g:'客户', cls:'g-cust', items:[['g-user','建档'],['g-cal','预约'],['g-bell','回访'],['g-users','管户']] },
    { g:'日终', cls:'g-day', items:[['g-money','结算缴款'],['g-doc','业务补录'],['g-list','验单处理'],['g-trace','操作留痕']] }
  ],
  P4: [
    { g:'接入身份', cls:'g-access', items:[['g-scan','扫码接入'],['g-seat','叫号'],['g-cal','预约查询']] },
    { g:'会话', cls:'g-session', items:[['g-plus','新建会话'],['g-take','接管'],['g-resume','断点续办'],['g-transfer','转台席']] },
    { g:'厅堂', cls:'g-item', items:[['g-flow','客户分流'],['g-seat','叫号管理'],['g-cal','预约登记'],['g-verify','巡检']] },
    { g:'依据核验', cls:'g-evidence', items:[['g-verify','材料预检'],['g-rule','引导规则'],['g-trace','留痕']] },
    { g:'工具', cls:'g-tool', items:[['g-print','打印凭条'],['g-bell','评价器'],['g-eye','模型观测']] }
  ]
};

(function () {
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
  function showPane(hash) {
    var btn = document.querySelector('#subNav button[data-sub="' + hash + '"]');
    if (btn) { btn.click(); return; }
    var panes = document.querySelectorAll('.subpane');
    if (!panes.length) { location.hash = hash; return; }
    for (var i = 0; i < panes.length; i++) {
      panes[i].hidden = panes[i].getAttribute('data-pane') !== hash;
    }
    location.hash = hash;
  }
  function note(name) {
    var host = document.getElementById('rct') || document.body;
    var old = document.getElementById('hallGoNote');
    if (old) old.parentNode.removeChild(old);
    var n = document.createElement('div');
    n.id = 'hallGoNote';
    n.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);background:#243028;color:#fff;border-radius:8px;padding:10px 14px;font-size:13px;z-index:80';
    n.textContent = name + ' · 记在本页，没有另一张表';
    host.appendChild(n);
    setTimeout(function () { if (n.parentNode) n.parentNode.removeChild(n); }, 2200);
  }
  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('#ribbon .rb');
    if (!b) return;
    var span = b.querySelector('span');
    var name = (span ? span.textContent : b.textContent || '').replace(/\s+/g, '');
    var role = roleOf();
    if (!role || !window.HALL_GO) return;
    var dest = (window.HALL_GO[role] || {})[name];
    if (!dest) {
      if (role === 'P5') { e.preventDefault(); e.stopImmediatePropagation(); note(name); }
      return;
    }
    e.preventDefault();
    e.stopImmediatePropagation();
    var file = dest;
    var hash = '';
    var cut = dest.indexOf('#');
    if (cut >= 0) { file = dest.slice(0, cut); hash = dest.slice(cut + 1); }
    if (file === hereFile()) { if (hash) showPane(hash); return; }
    location.href = dest.indexOf(window.PAGE_BASE) === 0 ? dest : window.PAGE_BASE + dest;
  }, true);
})();


