# 后端骨架

单后端。入口 `app/main.py` 的 `create_app` 尚未接 HTTP 框架。能力、厅堂服务和内存仓储已能互调，不连库、不调用模型。页面等壳子接入。

```text
app/
  gateway/       请求管道 · trace_id · 写操作 ID · fail-closed
  auth/          can(role, action)；登录分流以后接这里
  session/       会话中枢（内存进度；会话留原网点）
  orchestration/ Supervisor 留位
  capabilities/  公有能力＋五岗工具（扫描／称重／授权／叫号）
  services/      公有服务：到期转存业务链
  assembly/      五岗工具表，页面以后按 id 接
  provider/      模型档案；本地 deepseek-r1:1.5b 已试通
  admin/         观测台＋岗位／能力表骨架（只读）
  storage/       业务库／向量库／checkpoint／审计留位
```
