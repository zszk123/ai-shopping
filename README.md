# AI Shopping

AI Shopping 是一个面向电商场景的智能比价系统，包含 Flutter 前端、FastAPI 后端、AI 商品识别/分析、比价历史、AI 客服和基础工程化配置。

## 项目结构

```text
ai-shopping/
  backend/    FastAPI 后端服务
  frontend/   Flutter 前端应用
  design/     UI 设计稿与设计说明
  docs/       项目文档可按需补充
```

## 后端启动

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

后端默认地址：

```text
http://127.0.0.1:8000
```

## 前端启动

```powershell
cd frontend
flutter pub get
flutter run -d chrome
```

安卓真机调试时先做端口转发：

```powershell
E:\AndroidSDK\platform-tools\adb.exe reverse tcp:8000 tcp:8000
flutter run -d 你的设备ID
```

## 环境变量

后端需要复制示例配置：

```powershell
cd backend
copy .env.example .env
```

然后填写本地数据库、Redis、Milvus、DashScope、OSS 等配置。

注意：`.env` 不能提交到 GitHub。

## 提交前检查

```powershell
git status --ignored --short
git check-ignore -v backend/.env
```

确认 `.env`、`.venv`、`build`、`.dart_tool`、`.gradle-cache` 等文件处于忽略状态后再提交。
