# 本机两个库

初步业务库是本目录的 `biz.sqlite`：员工按五合一原型名册，客户 50 条存完整证件、手机和住址。管理员走 `/api/customers?role=P5` 只拿到掩码。本机 3306 的 MySQL 服务在跑，但还没有 `zhiyou` 账号，所以这一步没有改那台库。

写代码时不用启动。要建表或联调时，在本目录执行：

```bat
docker compose up -d
```

首次启动会跑 `sql/` 里的脚本，建成 `biz` 和 `session`。Chroma 监听 `8000`，业务进程用 HttpClient 去连，不要用 `PersistentClient`。

测完可以 `docker compose stop`。密码只供本机，部署到邮政机器前要换掉，并改 `settings.example.env` 里的主机名。
