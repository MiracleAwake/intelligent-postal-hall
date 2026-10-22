-- 会话进度。与业务库同机不同库，挂网点，不随人跨网点带走。

CREATE DATABASE IF NOT EXISTS session
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE session;

CREATE TABLE IF NOT EXISTS session_state (
  id                     CHAR(36)     NOT NULL,
  org_id                 BIGINT UNSIGNED NOT NULL COMMENT '原网点，跨库指针',
  post_id                BIGINT UNSIGNED NULL,
  external_customer_ref  VARCHAR(128) NULL COMMENT '客户档案编号，不存底库副本',
  progress_json          JSON         NOT NULL,
  status                 VARCHAR(32)  NOT NULL DEFAULT 'active',
  updated_at             DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_session_org (org_id)
) ENGINE=InnoDB;
