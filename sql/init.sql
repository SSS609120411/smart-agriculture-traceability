-- =============================================================
-- 智慧农产品溯源管理系统 数据库初始化脚本
-- 使用方式（二选一）：
--   1) 命令行：mysql -u root -p < init.sql
--   2) MySQL 客户端（Navicat/Workbench 等）打开并执行本文件
--
-- 说明：本脚本只建库建表；种子数据（管理员账号、示例产品/批次）
--       请随后运行 backend 下的 seed.py 生成（含正确的密码哈希）。
-- =============================================================

CREATE DATABASE IF NOT EXISTS traceability
  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE traceability;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  username      VARCHAR(64)  NOT NULL UNIQUE,
  password_hash VARCHAR(256) NOT NULL,
  role          VARCHAR(20)  NOT NULL DEFAULT 'consumer',
  name          VARCHAR(64),
  phone         VARCHAR(20),
  created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 产品分类表
CREATE TABLE IF NOT EXISTS categories (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  name        VARCHAR(64) NOT NULL UNIQUE,
  description VARCHAR(256)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 产品表
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

-- 批次表（核心溯源单元）
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

-- 种植（农事）记录表
CREATE TABLE IF NOT EXISTS planting_records (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  batch_id    INT NOT NULL,
  record_type VARCHAR(32),
  detail      VARCHAR(512),
  record_date VARCHAR(20),
  location    VARCHAR(128),
  CONSTRAINT fk_planting_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 质检记录表
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

-- 加工记录表
CREATE TABLE IF NOT EXISTS processing_records (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  batch_id     INT NOT NULL,
  process_date VARCHAR(20),
  process_type VARCHAR(64),
  detail       VARCHAR(512),
  operator     VARCHAR(64),
  CONSTRAINT fk_processing_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 物流记录表
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

-- 销售记录表
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

-- 溯源查询日志表
CREATE TABLE IF NOT EXISTS trace_logs (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  batch_id   INT NOT NULL,
  query_time DATETIME DEFAULT CURRENT_TIMESTAMP,
  ip         VARCHAR(64),
  CONSTRAINT fk_tracelog_batch FOREIGN KEY (batch_id) REFERENCES batches (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
