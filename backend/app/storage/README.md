# 持久化（形态已定）

| 层 | 怎么放 | 本机 |
|----|--------|------|
| 业务库 `biz` | 独立 MySQL | 人、岗、任职、业绩（`staff_id`）、管户与任务（`post_id`）、审计留位 |
| 会话库 `session` | 同一台 MySQL 的另一个库 | 进度挂 `org_id`，不随人跨网点 |
| 向量库 | 独立 Chroma，HttpClient | `chromadb/chroma`，端口 8000 |

四平台底库不建表，只存 `source_system` + `external_id`。

脚本在 [`../../deploy/`](../../deploy/)。组装前还要补哪些表，见 [`../../../../参考资料/数据库/库表预想.md`](../../../../参考资料/数据库/库表预想.md)。地址样例：`settings.example.env`。`describe_pipes()` 只报这三条管道的地址，`connected` 恒为假。`MemoryBiz` 按同一批表在内存里执行归属规则。导入本包不会去连库。
