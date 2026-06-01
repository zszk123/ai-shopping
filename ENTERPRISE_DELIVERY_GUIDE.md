# AI Shopping 项目企业级交付学习文档

这份文档用“小白也能看懂”的方式解释：为什么要这样改、每个文件负责什么、上线前怎么检查。

## 1. 这次做了什么

项目分成两个仓库：

- `backend`：后端，负责登录、比价、AI 识图、向量搜索、爬虫管理。
- `frontend`：前端，负责手机 App / Web 页面。

这次把项目从“能跑的 Demo”往“可以上线交付的工程”推进，重点做了这些：

- 清理后端 Git 里已经跟踪的 `__pycache__/*.pyc`，这些是本地运行生成物，不应该提交。
- 重写后端 `.gitignore`，防止 `.env`、虚拟环境、缓存、测试覆盖率等文件进入仓库。
- 增加后端生产配置校验，生产环境必须配置强 `JWT_SECRET`、明确 `CORS_ORIGINS` 和内部接口令牌。
- 增加 `/healthz` 和 `/readyz`，上线后可以让服务器或网关判断服务是否健康。
- 增加 Alembic 数据库迁移，生产环境不再依赖 `create_all()` 自动建表。
- 增加 Dockerfile、docker-compose，方便本地或服务器部署。
- 增加 GitHub Actions CI，提交代码时自动跑 lint 和测试。
- 给登录/注册加基础限流，降低被暴力猜密码的风险。
- 给内部爬虫和向量接口加 `X-Internal-Token` 保护。
- 给图片上传加文件头校验，不能只相信浏览器传来的 `content_type`。
- 修复用户密码字段长度，避免更安全的密码 hash 存不下。

## 2. 为什么这些是企业级必需品

`.env` 不能进 Git，因为里面通常有数据库密码、JWT 密钥、云服务 Key。一旦提交到远程仓库，就相当于把钥匙放在门口。

`__pycache__`、`.venv`、`build` 这类文件不能进 Git，因为它们是机器生成的，每个人电脑上都不一样。提交进去会让代码审查很乱，也会让仓库越来越大。

数据库迁移很重要。Demo 可以启动时自动建表，但生产环境不能这样做。企业项目需要知道“这次上线改了哪张表、能不能回滚、什么时候执行”。

健康检查很重要。`/healthz` 说明进程还活着，`/readyz` 说明数据库和 Redis 也连得上。部署平台可以根据这些接口决定要不要把流量打到这台机器。

CI 很重要。它像一个自动检查员，每次提交代码都帮你跑格式检查、静态分析和测试，避免“我电脑能跑，服务器不能跑”。

## 3. 后端怎么启动

进入后端目录：

```bash
cd backend
```

创建虚拟环境并安装依赖：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

复制环境变量模板：

```bash
copy .env.example .env
```

启动：

```bash
uvicorn app.main:app --reload
```

打开接口文档：

```text
http://127.0.0.1:8000/docs
```

## 4. 数据库迁移怎么用

生产环境建表：

```bash
alembic upgrade head
```

以后你改了 `app/models` 里的表结构，就生成一份迁移：

```bash
alembic revision --autogenerate -m "add some column"
```

然后再执行：

```bash
alembic upgrade head
```

可以把 Alembic 理解成“数据库版本管理工具”，它像 Git 管代码一样管理表结构。

## 5. Docker 怎么用

后端目录里现在有：

- `Dockerfile`：告诉 Docker 怎么构建后端镜像。
- `docker-compose.yml`：一键拉起 MySQL、Redis 和后端。

启动：

```bash
docker compose up --build
```

停止：

```bash
docker compose down
```

## 6. 前端怎么启动

进入前端目录：

```bash
cd frontend
```

安装依赖并启动：

```bash
flutter pub get
flutter run
```

指定后端地址：

```bash
flutter run --dart-define=API_BASE_URL=http://127.0.0.1:8000
```

开发时后端没准备好，可以打开 mock fallback：

```bash
flutter run --dart-define=USE_MOCK_ON_API_FAILURE=true
```

## 7. 上线前检查清单

后端：

- `.env` 已经配置真实数据库、Redis、OSS、DashScope。
- `ENV=production`。
- `JWT_SECRET` 至少 32 位，并且不是模板值。
- `INTERNAL_API_TOKEN` 已配置，并且只给内部系统使用。
- `CORS_ORIGINS` 只填你的前端域名，不要用 `*`。
- 已执行 `alembic upgrade head`。
- `/healthz` 返回 `code=200`。
- `/readyz` 返回 `code=200`。

前端：

- `API_BASE_URL` 指向生产后端地址。
- 关闭 `USE_MOCK_ON_API_FAILURE`。
- 跑过 `flutter analyze` 和 `flutter test`。

## 8. 你接下来学习的顺序

建议按这个顺序学：

1. 先看 `.gitignore`，理解什么文件不该提交。
2. 再看 `.env.example`，理解配置和代码为什么要分开。
3. 看 `app/main.py`，理解服务启动、健康检查、中间件。
4. 看 `app/dependencies.py`，理解登录校验、内部接口令牌、限流。
5. 看 `migrations/versions`，理解数据库迁移。
6. 看 `.github/workflows`，理解 CI 自动检查。
7. 最后看 `Dockerfile` 和 `docker-compose.yml`，理解部署。

这就是企业项目的核心思路：代码能跑只是第一步，更重要的是安全、可检查、可部署、可回滚、可协作。

