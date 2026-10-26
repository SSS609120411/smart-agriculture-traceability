-- =============================================================
-- PythonAnywhere 建表脚本（不要 CREATE DATABASE）
-- 使用方法：
--   1. 在 PythonAnywhere「Databases」页新建数据库（假设命名为 traceability），
--      实际库名为：你的用户名$traceability
--   2. 打开 MySQL 控制台，先执行：
--        USE 你的用户名$traceability;
--   3. 再把本文件内容粘贴执行。
-- =============================================================

CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(64)  NOT NULL UNIQUE,
  password_hash VARCHAR(256) NOT NULL,
  role          VARCHAR(20)  NOT NULL DEFAULT 'consumer',
  name          VARCHAR(64),
  phone         VARCHAR(20),
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(64) NOT NULL UNIQUE,
  description VARCHAR(256)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  category_id INT NOT NULL,
  name        VARCHAR(128) NOT NULL,
  origin      VARCHAR(128),
  variety     VARCHAR(128),
  description VARCHAR(512),
  image_url   VARCHAR(256),
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES categories (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS batches (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  product_id      INT NOT NULL,
  producer_id     INT NOT NULL,
  trace_code      VARCHAR(64) NOT NULL UNIQUE,
  qr_code         VARCHAR(256),
  production_date VARCHAR(20),
  quantity        VARCHAR(64),
  unit            VARCHAR(20),
  status          VARCHAR(20) DEFAULT '生产中',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_batch_product  FOREIGN KEY (product_id)  REFERENCES products (id),
  CONSTRAINT fk_batch_producer FOREIGN KEY (producer_id) REFERENCES users (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS planting_records (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  batch_id    INT NOT NULL,
  record_type VARCHAR(32),
  detail      VARCHAR(512),
  record_date VARCHAR(20),
  location    VARCHAR(128),
  CONSTRAINT fk_planting_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS quality_inspections (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  batch_id     INT NOT NULL,
  inspect_date VARCHAR(20),
  inspector    VARCHAR(64),
  items        VARCHAR(256),
  result       VARCHAR(20),
  report_url   VARCHAR(256),
  CONSTRAINT fk_quality_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS processing_records (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  batch_id     INT NOT NULL,
  process_date VARCHAR(20),
  process_type VARCHAR(64),
  detail       VARCHAR(512),
  operator     VARCHAR(64),
  CONSTRAINT fk_processing_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS logistics_records (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  batch_id       INT NOT NULL,
  transport_date VARCHAR(20),
  from_place     VARCHAR(128),
  to_place       VARCHAR(128),
  carrier        VARCHAR(64),
  temperature    VARCHAR(32),
  CONSTRAINT fk_logistics_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS sales_records (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  batch_id  INT NOT NULL,
  sale_date VARCHAR(20),
  channel   VARCHAR(64),
  quantity  VARCHAR(64),
  price     VARCHAR(32),
  buyer     VARCHAR(128),
  CONSTRAINT fk_sales_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS trace_logs (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  batch_id   INT NOT NULL,
  query_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip         VARCHAR(64),
  CONSTRAINT fk_tracelog_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
