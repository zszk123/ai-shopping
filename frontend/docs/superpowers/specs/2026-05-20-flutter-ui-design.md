# AI智能比价助手 — Flutter移动端UI设计文档

**日期**: 2026-05-20
**框架**: Flutter + Riverpod + go_router
**数据策略**: Mock data built-in (后端未就绪)

---

## 一、技术选型

| 层 | 选型 | 用途 |
|---|---|---|
| 框架 | Flutter 3.x | 跨平台移动端 |
| 路由 | go_router | 声明式路由，支持deep link |
| 状态管理 | flutter_riverpod | 每个feature独立Provider |
| 图表 | fl_chart | 30天价格走势折线图 |
| 图片选择 | image_picker | 拍照/相册 |
| HTTP | dio | 预留（当前Mock拦截） |
| 本地存储 | shared_preferences | token/用户缓存 |

## 二、主题色彩规范

| 用途 | 色值 | 说明 |
|---|---|---|
| 主色调 | `#1677FF` | 按钮、高亮、标题强调 |
| 价格红 | `#FF4D4F` | 券后到手价 |
| 降价绿 | `#52C41A` | 价格降低标记 |
| 背景色 | `#F7F8FA` | 全局背景 |
| 卡片 | 白色 `#FFFFFF` | 12px圆角 + 轻微阴影(elevation: 2) |
| 文字主色 | `#333333` | 标题正文 |
| 文字辅色 | `#999999` | 说明文字、时间 |

## 三、路由设计

```
/login            → 登录注册页
/home             → 首页 (底部Tab: 首页)
/camera           → 拍照/相册选择页
/compare-result   → 比价结果页 (核心)
/history          → 比价历史页 (底部Tab: 比价历史)
/profile          → 个人中心页 (底部Tab: 我的)
```

**ShellRoute**: `/home`、`/history`、`/profile` 共享底部Tab导航栏，Tab切换保持状态。

## 四、目录结构 (Feature-first)

```
lib/
├── main.dart
├── app.dart                    # MaterialApp + 主题配置
├── router.dart                 # GoRouter 路由配置
├── features/
│   ├── auth/
│   │   ├── login_page.dart     # 登录注册页
│   │   └── auth_provider.dart  # 登录状态管理
│   ├── home/
│   │   ├── home_page.dart      # 首页 (搜索框 + 3个入口卡片)
│   │   └── home_provider.dart
│   ├── camera/
│   │   ├── camera_page.dart    # 拍照/相册选择页
│   │   └── camera_provider.dart # 识别流程管理
│   ├── compare/
│   │   ├── compare_page.dart   # 比价结果页 (核心)
│   │   ├── compare_provider.dart
│   │   └── widgets/
│   │       ├── product_card.dart     # 识别商品卡片
│   │       ├── ai_analysis_card.dart # AI分析卡片
│   │       ├── price_chart.dart       # 30天价格走势图
│   │       └── same_list_item.dart    # 同款商品列表项
│   ├── history/
│   │   ├── history_page.dart   # 比价历史页
│   │   └── history_provider.dart
│   └── profile/
│       ├── profile_page.dart   # 个人中心页
│       └── profile_provider.dart
├── shared/
│   ├── theme.dart              # 主题定义 (Color, TextTheme, CardTheme)
│   ├── widgets/
│   │   ├── app_scaffold.dart   # 带Tab的页面壳
│   │   ├── search_bar.dart     # 通栏搜索框
│   │   └── loading_overlay.dart # 加载蒙层
│   ├── models/
│   │   ├── user.dart
│   │   ├── goods.dart          # 商品模型
│   │   ├── compare_result.dart # 比价结果模型
│   │   └── history_record.dart # 历史记录模型
│   └── mock/
│       ├── mock_users.dart
│       ├── mock_goods.dart
│       └── mock_compare.dart   # Mock比价数据
```

## 五、页面设计

### 5.1 登录注册页 (`/login`)

**组件树**:
```
LoginPage
├── Logo + 标题 "AI智能比价助手" + 副标题 "拍照识图 全网比价"
├── TabBar (登录 | 注册) — 控制下方表单切换
├── TextField (手机号)
├── TextField (密码, obscure)
├── [仅注册模式] TextField (确认密码)
├── [仅注册模式] TextField (昵称)
├── ElevatedButton "登录/注册" (#1677FF, 圆角24px, 全宽)
└── Text "登录即同意《隐私政策》" (字号12, #999)
```

**状态**: `authProvider` — loginMode / isLoading / errorMsg
**交互**: 成功 → `context.go('/home')`

### 5.2 首页 (`/home`)

**组件树**:
```
HomePage (with BottomTab: 首页高亮)
├── SearchBar (通栏, hint: "输入商品名称搜索比价")
├── Card 1: 拍照识图比价 (最大, 相机图标, 渐变色背景)
│   └── onTap → /camera
├── Card 2: 链接比价 (链接图标)
│   └── onTap → Dialog输入URL → /compare-result
├── Card 3: 关键词搜索比价 (搜索图标)
│   └── onTap → Dialog输入关键词 → /compare-result
└── [搜索框onSubmit] → /compare-result?keyword=xxx
```

### 5.3 拍照/相册选择页 (`/camera`)

**组件树**:
```
CameraPage
├── AppBar (返回 + 标题"选择图片识别")
├── Row (两个按钮横向排列)
│   ├── ElevatedButton "拍照" (icon: camera)
│   └── ElevatedButton "从相册选择" (icon: photo)
└── [识别时] LoadingOverlay
    ├── CircularProgressIndicator
    ├── Text "AI识别中..."
    └── Text "全网检索中..."
→ 完成 → context.go('/compare-result', extra: result)
```

### 5.4 比价结果页 (`/compare-result`) — 核心

**组件树**:
```
CompareResultPage (ScrollView)
├── AppBar (返回 + 标题"比价结果")
├── ProductCard
│   ├── Image (商品缩略图)
│   ├── Text (商品名称)
│   └── Text (品牌·型号, #999)
├── AiAnalysisCard
│   ├── Label "AI入手建议"
│   ├── Text (建议: 值得入手/再等等/不建议)
│   ├── Row: "当前价位 ¥299" / "历史最低 ¥259"
│   └── Text (趋势: 价格平稳/上涨/下跌)
├── PriceChart
│   └── fl_chart LineChart (30天走势, 主色填充)
├── Text "全网同款 (按价格升序)" — 列表标题
└── ListView (同款列表, 不可滚动, shrinkWrap)
    └── SameListItem × N
        ├── Row
        │   ├── 平台Logo (jd/taobao/pdd/douyin)
        │   ├── Image (商品图, 60x60)
        │   ├── Column
        │   │   ├── Text (名称·规格)
        │   │   └── Text (店铺·销量)
        │   ├── Column (右对齐)
        │   │   ├── Text ("¥299", 红色#FF4D4F, 粗体)
        │   │   └── ElevatedButton "立即购买"
        │   └── [下架商品: 整体opacity 0.4, 无购买按钮]
        └── Divider
```

**排序规则**: 按 `real_price` (券后到手价) 升序
**下架商品**: 置灰 (`ColorFilter` + `Opacity`)，价格划线，隐藏购买按钮
**列表优化**: 使用 `ListView.builder` + `shrinkWrap: true` + `NeverScrollableScrollPhysics`

### 5.5 比价历史页 (`/history`)

**组件树**:
```
HistoryPage (with BottomTab: 比价历史高亮)
├── AppBar (标题"比价历史" + TextButton"清空全部")
├── [空态] Center: Icon + Text "暂无记录"
└── [非空] ListView.builder
    └── HistoryCard × N
        ├── Leading: Icon (📷/🔗/🔍, 按compare_type)
        ├── Title: search_source (截断)
        ├── Subtitle: create_time
        ├── Trailing: IconButton (删除, 🗑)
        └── onTap → 重新执行比价 → /compare-result (最新数据)
```

**状态**: `historyProvider` — list / isLoading / isEmpty
**核心逻辑**: 历史表只存 `search_source` + `compare_type`，点击时重新调比价接口

### 5.6 个人中心页 (`/profile`)

**组件树**:
```
ProfilePage (with BottomTab: 我的高亮)
├── UserInfoCard
│   ├── CircleAvatar (头像, 默认渐变色)
│   ├── Column
│   │   ├── Text (昵称)
│   │   └── Text (手机号, 脱敏 138****1234)
│   └── Icon (编辑资料 >)
├── MenuList
│   ├── ListTile "我的比价历史" → /history
│   ├── ListTile "关于我们"
│   ├── ListTile "版本 1.0.0"
│   └── ListTile "隐私政策"
└── OutlinedButton "退出登录" (红色边框)
    └── onTap → Dialog确认 → authProvider.logout() → /login
```

## 六、数据流设计

### Mock数据策略

```
Mock层拦截模拟所有API调用:
- POST /api/user/login → 返回固定JWT + 用户信息
- POST /api/compare/image → 模拟2秒延迟后返回比价结果
- POST /api/compare/url → 同上
- GET  /api/compare/search → 同上
- GET  /api/record/list → 返回本地存储的历史mock数据
- DELETE /api/record/delete → 删除mock数据
- GET  /api/goods/price/history → 返回30天mock价格数组
```

### Provider依赖图

```
authProvider (独立)
  ↓ (login后)
homeProvider → 搜索/导航
  ↓
cameraProvider → 拍照/选图 → 模拟识别
  ↓
compareProvider → 接收结果数据
  ↓ (用户操作保存)
historyProvider → 管理历史列表
profileProvider → 用户信息CRUD
```

## 七、交互规范

1. **比价历史只存源头**: 不存结果快照，点击重新检索实时最新数据
2. **下架商品置灰**: `sale_status=0`的商品降低透明度，移除购买按钮
3. **价格排序**: 按 `real_price` 券后到手价升序排列
4. **AI分析必须展示**: 入手建议 + 当前价位 + 历史最低 + 趋势
5. **30天价格走势折线图**: 使用fl_chart，主色填充区域
6. **加载状态**: 搜索/识别时显示loading蒙层 + 文字提示
7. **空态处理**: 历史记录为空时显示 "暂无记录" 图标+文字
8. **错误处理**: 网络错误时SnackBar提示，不阻断页面

## 八、Mock数据规模

| 数据 | 数量 |
|---|---|
| 用户 | 3个mock用户 |
| 商品(比价结果) | 每搜索返回 5-8 个同款商品 |
| 价格历史 | 每商品 30 条日记录 |
| 历史记录 | 初始 3-5 条mock记录 |
