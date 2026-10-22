-- 业务库。五个岗位的增删改查都进这里。
-- 业绩挂人，客户关系与任务挂岗位，调岗只改任职，不改这两类行。

CREATE DATABASE IF NOT EXISTS biz
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE biz;

CREATE TABLE IF NOT EXISTS org (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  code          VARCHAR(64)  NOT NULL,
  name          VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_org_code (code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS staff (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  employee_no   VARCHAR(64)  NOT NULL,
  name          VARCHAR(64)  NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_staff_no (employee_no)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS post (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  org_id        BIGINT UNSIGNED NOT NULL,
  role_code     VARCHAR(8)   NOT NULL COMMENT 'P1～P5',
  title         VARCHAR(128) NOT NULL,
  PRIMARY KEY (id),
  KEY idx_post_org (org_id),
  CONSTRAINT fk_post_org FOREIGN KEY (org_id) REFERENCES org (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS assignment (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  staff_id      BIGINT UNSIGNED NOT NULL,
  post_id       BIGINT UNSIGNED NOT NULL,
  started_at    DATETIME     NOT NULL,
  ended_at      DATETIME     NULL,
  PRIMARY KEY (id),
  KEY idx_asg_staff (staff_id),
  KEY idx_asg_post (post_id),
  CONSTRAINT fk_asg_staff FOREIGN KEY (staff_id) REFERENCES staff (id),
  CONSTRAINT fk_asg_post FOREIGN KEY (post_id) REFERENCES post (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS performance_entry (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  staff_id      BIGINT UNSIGNED NOT NULL COMMENT '随人，调岗不改',
  subject       VARCHAR(64)  NOT NULL,
  amount        DECIMAL(18,2) NULL,
  note          VARCHAR(255) NULL,
  occurred_at   DATETIME     NOT NULL,
  PRIMARY KEY (id),
  KEY idx_perf_staff (staff_id),
  CONSTRAINT fk_perf_staff FOREIGN KEY (staff_id) REFERENCES staff (id)
) ENGINE=InnoDB COMMENT='本期只记入口，不做各地核算';

CREATE TABLE IF NOT EXISTS customer_binding (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  post_id         BIGINT UNSIGNED NOT NULL COMMENT '随岗位，调岗不带走',
  source_system   VARCHAR(64)  NOT NULL COMMENT '四平台之一，底库不搬',
  external_id     VARCHAR(128) NOT NULL,
  display_name    VARCHAR(128) NULL,
  PRIMARY KEY (id),
  UNIQUE KEY uk_binding (post_id, source_system, external_id),
  CONSTRAINT fk_bind_post FOREIGN KEY (post_id) REFERENCES post (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS task_item (
  id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  post_id       BIGINT UNSIGNED NOT NULL COMMENT '随岗位，接任者继承',
  title         VARCHAR(255) NOT NULL,
  status        VARCHAR(32)  NOT NULL DEFAULT 'open',
  session_id    CHAR(36)     NULL COMMENT '指向 session 库，跨库不设外键',
  PRIMARY KEY (id),
  KEY idx_task_post (post_id),
  CONSTRAINT fk_task_post FOREIGN KEY (post_id) REFERENCES post (id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS audit_event (
  id              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  trace_id        VARCHAR(64)  NOT NULL,
  op_id           VARCHAR(64)  NOT NULL,
  action          VARCHAR(64)  NOT NULL,
  actor_staff_id  BIGINT UNSIGNED NULL,
  created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_audit_trace (trace_id)
) ENGINE=InnoDB COMMENT='留位：先记意图。不实现破玻璃';

CREATE TABLE IF NOT EXISTS prompt_iteration (
  post_id       BIGINT UNSIGNED NOT NULL COMMENT '一份现行正文，随岗位',
  role_code     VARCHAR(8)   NOT NULL,
  body          TEXT         NOT NULL,
  updated_at    DATETIME     NOT NULL,
  PRIMARY KEY (post_id),
  CONSTRAINT fk_prompt_post FOREIGN KEY (post_id) REFERENCES post (id)
) ENGINE=InnoDB COMMENT='迭代提示词。不存流水账';
