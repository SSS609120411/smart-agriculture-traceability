# 智慧农产品溯源管理系统

面向「从农田到餐桌」的农产品全链路溯源系统：生产者录入产品与批次，系统为每个批次生成**唯一溯源码 + 二维码**，记录 **生产 → 质检 → 加工 → 物流 → 销售** 各环节信息，消费者扫码或输码即可查看完整溯源链条。

> 软件工程实践课程项目 · 农业方向自选题目

## 技术栈

| 层 | 技术 |
|----|------|
| 后端 | Python Flask 2.2 + Flask-SQLAlchemy + PyJWT |
| 前端 | Vue 3 + Vite + Element Plus + Pinia + ECharts |
| 数据库 | MySQL 8.0（兼容 SQLite 便于本地自测） |
| 二维码 | qrcode + Pillow |

## 功能特性

- **角色权限**：管理员 / 生产者 / 消费者，JWT 认证 + 接口级角色校验
- **产品与分类管理**：农产品分类、产品（产地/品种）维护
- **批次管理**：创建批次自动生成唯一溯源码 + 二维码（可下载）
- **全链路记录**：种植（播种/施肥/用药/灌溉/采摘）、质检、加工、物流、销售
- **溯源查询**：公开接口，扫码/输码展示时间轴式溯源链条
- **数据看板**：产品分类分布、批次状态分布、各环节记录统计
- **用户管理**：管理员可增删改用户并分配角色

## 目录结构

```
智慧农产品溯源管理系统/
├── backend/            # Flask 后端
│   ├── app.py          # 入口
│   ├── config.py       # 配置（读 .env）
│   ├── models.py       # 10 张表 ORM 模型
│   ├── routes/         # 各模块接口
│   ├── utils/          # JWT / 二维码 / 响应
│   ├── seed.py         # 建表 + 种子数据
│   ├── smoke_test.py   # 冒烟测试
│   └── .env.example    # 配置模板
├── frontend/           # Vue3 前端
│   └── src/
│       ├── views/      # 页面
│       ├── router/     # 路由 + 权限守卫
│       ├── stores/     # Pinia 登录态
│       └── api/        # Axios 封装
├── sql/init.sql        # 建库建表脚本（自行执行）
└── docs/               # 完整设计文档
```

## 环境要求

- Python 3.9+（本项目基于 3.11）
- Node.js 18+、npm
- MySQL 8.0

## 快速启动

### 1. 初始化数据库（任选其一）

**方式 A（推荐）：MySQL**

1. 执行建库建表脚本：
   ```bash
   mysql -u root -p < sql/init.sql
   ```
2. 在 `backend/` 下复制配置模板并填写你的 MySQL 账号密码：
   ```bash
   cd backend
   copy .env.example .env    # 编辑 .env，改 MYSQL_USER / MYSQL_PASSWORD
   ```

**方式 B：SQLite（无需 MySQL，仅本地演示）**

在 `backend/.env` 中取消 `DATABASE_URL=sqlite:///traceability.db` 一行注释。

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python seed.py        # 建表 + 写入种子数据（管理员/示例批次）
python app.py         # 启动，监听 http://127.0.0.1:5000
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev           # 启动，浏览器访问 http://127.0.0.1:5173
```

## 演示账号

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |
| 生产者 | producer | producer123 |
| 消费者 | consumer | consumer123 |

## 溯源演示

- 登录 `producer` → 「批次管理」可看到示例批次「有机草莓」，点「二维码」扫码，或
- 直接在「溯源查询」页输入示例批次溯源码（`seed.py` 运行时会打印），查看全链路时间轴。

## 在线部署（GitHub + PythonAnywhere）

- 前端部署到 **GitHub Pages**，后端与 MySQL 部署到 **PythonAnywhere**。
- 详细步骤见 [`docs/07_在线部署指南.md`](docs/07_在线部署指南.md)；
- 相关配置文件：`.github/workflows/deploy-pages.yml`、`deploy/pythonanywhere_wsgi.py`、`deploy/pa_init.sql`。

## 注意事项

1. **手机扫码**：二维码内容默认指向 `http://127.0.0.1:5173`，仅本机有效。若需手机扫码演示，请将 `backend/.env` 中 `TRACE_PAGE_PREFIX` 改为电脑的局域网 IP（如 `http://192.168.1.100:5173/#/trace/`）。
2. **密码安全**：`.env` 中的 `SECRET_KEY` 建议改成随机字符串。
3. 完整设计文档见 `docs/` 目录。
