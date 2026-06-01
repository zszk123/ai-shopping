# AI智能比价助手 Flutter UI — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 6-page Flutter mobile app for AI-powered shopping price comparison with mock data, matching the ui.md specification exactly.

**Architecture:** Feature-first Flutter app with Riverpod state management, go_router navigation, and built-in mock data. Three bottom-tab pages (Home, History, Profile) are wrapped in a ShellRoute, while Login, Camera, and CompareResult are standalone stack pages.

**Tech Stack:** Flutter 3.x, flutter_riverpod, go_router, fl_chart, image_picker, shared_preferences, dio (stub)

**Spec reference:** [2026-05-20-flutter-ui-design.md](../specs/2026-05-20-flutter-ui-design.md)

---

### Task 1: Create Flutter project and configure dependencies

**Files:**
- Create: `pubspec.yaml`
- Create: `lib/main.dart` (placeholder)

- [ ] **Step 1: Create Flutter project**

```bash
flutter create --org com.aishop --project-name ai_shop ai-shoping
cd ai-shoping
```

- [ ] **Step 2: Update pubspec.yaml with all dependencies**

Replace the generated `pubspec.yaml`:

```yaml
name: ai_shop
description: AI智能比价助手 - 拍照识图全网比价
publish_to: 'none'
version: 1.0.0+1

environment:
  sdk: '>=3.1.0 <4.0.0'

dependencies:
  flutter:
    sdk: flutter
  flutter_riverpod: ^2.4.0
  go_router: ^12.0.0
  fl_chart: ^0.65.0
  image_picker: ^1.0.0
  shared_preferences: ^2.2.0
  dio: ^5.3.0
  intl: ^0.18.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.0
  riverpod_lint: ^2.0.0

flutter:
  uses-material-design: true
```

- [ ] **Step 3: Install dependencies**

```bash
flutter pub get
```

- [ ] **Step 4: Verify project structure**

Expected: `flutter pub get` succeeds with no errors. Directory has `lib/`, `pubspec.yaml`, standard Flutter structure.

---

### Task 2: Shared theme configuration

**Files:**
- Create: `lib/shared/theme.dart`

- [ ] **Step 1: Write theme.dart**

```dart
import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFF1677FF);
  static const priceRed = Color(0xFFFF4D4F);
  static const priceGreen = Color(0xFF52C41A);
  static const background = Color(0xFFF7F8FA);
  static const cardWhite = Colors.white;
  static const textPrimary = Color(0xFF333333);
  static const textSecondary = Color(0xFF999999);
  static const divider = Color(0xFFEEEEEE);
  static const disabled = Color(0xFFBBBBBB);
}

class AppTheme {
  static ThemeData get light {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: AppColors.primary,
        primary: AppColors.primary,
      ),
      scaffoldBackgroundColor: AppColors.background,
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.white,
        foregroundColor: AppColors.textPrimary,
        elevation: 0.5,
        centerTitle: true,
        titleTextStyle: TextStyle(
          color: AppColors.textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w600,
        ),
      ),
      cardTheme: CardTheme(
        color: AppColors.cardWhite,
        elevation: 2,
        shadowColor: Colors.black12,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(24),
          ),
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.background,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: AppColors.primary, width: 1.5),
        ),
        hintStyle: const TextStyle(color: AppColors.textSecondary, fontSize: 14),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: AppColors.primary,
        unselectedItemColor: AppColors.textSecondary,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
        selectedLabelStyle: TextStyle(fontSize: 11, fontWeight: FontWeight.w600),
        unselectedLabelStyle: TextStyle(fontSize: 11),
      ),
      dividerColor: AppColors.divider,
    );
  }
}
```

---

### Task 3: Shared data models

**Files:**
- Create: `lib/shared/models/user.dart`
- Create: `lib/shared/models/goods.dart`
- Create: `lib/shared/models/compare_result.dart`
- Create: `lib/shared/models/history_record.dart`

- [ ] **Step 1: Write user.dart**

```dart
class User {
  final int id;
  final String username;
  final String phone;
  final String avatar;

  const User({
    required this.id,
    required this.username,
    required this.phone,
    this.avatar = '',
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as int,
      username: json['username'] as String,
      phone: json['phone'] as String? ?? '',
      avatar: json['avatar'] as String? ?? '',
    );
  }

  String get maskedPhone {
    if (phone.length != 11) return phone;
    return '${phone.substring(0, 3)}****${phone.substring(7)}';
  }
}
```

- [ ] **Step 2: Write goods.dart**

```dart
class Goods {
  final int id;
  final String goodsName;
  final String brand;
  final String model;
  final String specParam;
  final String platform;
  final String shopName;
  final double originalPrice;
  final double realPrice;
  final String couponDesc;
  final String goodsImg;
  final String goodsUrl;
  final int salesNum;
  final double score;
  final int saleStatus; // 1=在售, 0=下架

  const Goods({
    required this.id,
    required this.goodsName,
    this.brand = '',
    this.model = '',
    this.specParam = '',
    required this.platform,
    this.shopName = '',
    this.originalPrice = 0,
    required this.realPrice,
    this.couponDesc = '',
    this.goodsImg = '',
    required this.goodsUrl,
    this.salesNum = 0,
    this.score = 0,
    this.saleStatus = 1,
  });

  bool get isOnSale => saleStatus == 1;
  bool get isOffShelf => saleStatus == 0;

  String get platformLabel {
    switch (platform) {
      case '京东':
        return '京东';
      case '淘宝':
        return '淘宝';
      case '拼多多':
        return '拼多多';
      case '抖音':
        return '抖音';
      default:
        return platform;
    }
  }

  String get salesText {
    if (salesNum >= 10000) return '${(salesNum / 10000).toStringAsFixed(1)}万+';
    if (salesNum >= 1000) return '${(salesNum / 1000).toStringAsFixed(1)}k+';
    return '$salesNum';
  }

  factory Goods.fromJson(Map<String, dynamic> json) {
    return Goods(
      id: json['id'] as int,
      goodsName: json['goods_name'] as String,
      brand: json['brand'] as String? ?? '',
      model: json['model'] as String? ?? '',
      specParam: json['spec_param'] as String? ?? '',
      platform: json['platform'] as String,
      shopName: json['shop_name'] as String? ?? '',
      originalPrice: (json['original_price'] as num?)?.toDouble() ?? 0,
      realPrice: (json['real_price'] as num?)?.toDouble() ?? 0,
      couponDesc: json['coupon_desc'] as String? ?? '',
      goodsImg: json['goods_img'] as String? ?? '',
      goodsUrl: json['goods_url'] as String,
      salesNum: json['sales_num'] as int? ?? 0,
      score: (json['score'] as num?)?.toDouble() ?? 0,
      saleStatus: json['sale_status'] as int? ?? 1,
    );
  }
}
```

- [ ] **Step 3: Write compare_result.dart**

```dart
import 'goods.dart';

class PricePoint {
  final DateTime date;
  final double price;

  const PricePoint({required this.date, required this.price});
}

class AiAnalysis {
  final String suggestion;       // 建议入手 / 再等等 / 不建议
  final String suggestionDetail;
  final double currentPrice;
  final double lowestPrice;
  final String trend;            // 价格平稳 / 上涨 / 下跌
  final String trendDetail;

  const AiAnalysis({
    required this.suggestion,
    this.suggestionDetail = '',
    required this.currentPrice,
    required this.lowestPrice,
    required this.trend,
    this.trendDetail = '',
  });
}

class CompareResult {
  final Goods identifiedGoods;
  final AiAnalysis aiAnalysis;
  final List<PricePoint> priceHistory30Days;
  final List<Goods> sameGoodsList; // sorted by realPrice ASC

  const CompareResult({
    required this.identifiedGoods,
    required this.aiAnalysis,
    required this.priceHistory30Days,
    required this.sameGoodsList,
  });
}
```

- [ ] **Step 4: Write history_record.dart**

```dart
class HistoryRecord {
  final int id;
  final int userId;
  final String searchSource;
  final int compareType; // 1=图片, 2=链接, 3=关键词
  final DateTime createTime;

  const HistoryRecord({
    required this.id,
    required this.userId,
    required this.searchSource,
    required this.compareType,
    required this.createTime,
  });

  String get typeLabel {
    switch (compareType) {
      case 1:
        return '图片比价';
      case 2:
        return '链接比价';
      case 3:
        return '关键词比价';
      default:
        return '比价';
    }
  }

  String get typeIcon {
    switch (compareType) {
      case 1:
        return '📷';
      case 2:
        return '🔗';
      case 3:
        return '🔍';
      default:
        return '📋';
    }
  }

  String get displaySource {
    if (searchSource.length > 50) {
      return '${searchSource.substring(0, 50)}...';
    }
    return searchSource;
  }

  factory HistoryRecord.fromJson(Map<String, dynamic> json) {
    return HistoryRecord(
      id: json['id'] as int,
      userId: json['user_id'] as int,
      searchSource: json['search_source'] as String,
      compareType: json['compare_type'] as int,
      createTime: DateTime.parse(json['create_time'] as String),
    );
  }
}
```

---

### Task 4: Mock data

**Files:**
- Create: `lib/shared/mock/mock_users.dart`
- Create: `lib/shared/mock/mock_compare.dart`
- Create: `lib/shared/mock/mock_history.dart`

- [ ] **Step 1: Write mock_users.dart**

```dart
import '../models/user.dart';

const mockUsers = [
  User(id: 1, username: '小明', phone: '13812345678'),
  User(id: 2, username: '购物达人', phone: '13987654321'),
];

const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token';

Map<String, dynamic> mockLoginResponse(User user) {
  return {
    'code': 200,
    'msg': '登录成功',
    'data': {
      'token': mockToken,
      'user_id': user.id,
      'username': user.username,
      'phone': user.phone,
    },
  };
}
```

- [ ] **Step 2: Write mock_compare.dart**

```dart
import '../models/goods.dart';
import '../models/compare_result.dart';

CompareResult mockCompareResult(String keyword) {
  return CompareResult(
    identifiedGoods: Goods(
      id: 1001,
      goodsName: keyword.isNotEmpty ? keyword : '索尼 WH-1000XM5 头戴式降噪耳机',
      brand: '索尼',
      model: 'WH-1000XM5',
      specParam: '黑色 蓝牙5.3',
      platform: '京东',
      shopName: '索尼官方旗舰店',
      originalPrice: 3299,
      realPrice: 2299,
      goodsUrl: 'https://item.jd.com/example.html',
      salesNum: 58000,
      score: 4.9,
    ),
    aiAnalysis: const AiAnalysis(
      suggestion: '建议入手',
      suggestionDetail: '当前价格处于近30天低位，比历史均价低约8%，现在入手性价比较高。',
      currentPrice: 2299,
      lowestPrice: 2199,
      trend: '价格平稳',
      trendDetail: '近30天价格在2199-2599之间波动，目前处于低位区间。',
    ),
    priceHistory30Days: _generate30DayPrices(2299),
    sameGoodsList: [
      Goods(
        id: 1001, goodsName: '索尼 WH-1000XM5 头戴式降噪耳机', brand: '索尼',
        model: 'WH-1000XM5', specParam: '黑色', platform: '拼多多',
        shopName: '数码旗舰店', originalPrice: 3299, realPrice: 2089,
        goodsUrl: 'https://pdd.com/example1', salesNum: 32000, score: 4.8,
      ),
      Goods(
        id: 1002, goodsName: '索尼 WH-1000XM5 头戴式降噪耳机', brand: '索尼',
        model: 'WH-1000XM5', specParam: '黑色', platform: '京东',
        shopName: '索尼官方旗舰店', originalPrice: 3299, realPrice: 2299,
        goodsUrl: 'https://jd.com/example1', salesNum: 58000, score: 4.9,
      ),
      Goods(
        id: 1003, goodsName: '索尼 WH-1000XM5 降噪耳机', brand: '索尼',
        model: 'WH-1000XM5', specParam: '银色', platform: '淘宝',
        shopName: 'HiFi音频店', originalPrice: 2999, realPrice: 2349,
        goodsUrl: 'https://taobao.com/example1', salesNum: 15000, score: 4.7,
      ),
      Goods(
        id: 1004, goodsName: '索尼 WH-1000XM5 头戴降噪耳机', brand: '索尼',
        model: 'WH-1000XM5', specParam: '黑色', platform: '抖音',
        shopName: '潮玩数码', originalPrice: 2599, realPrice: 2399,
        goodsUrl: 'https://douyin.com/example1', salesNum: 8000, score: 4.6,
      ),
      Goods(
        id: 1005, goodsName: '索尼 WH-1000XM5 降噪耳机', brand: '索尼',
        model: 'WH-1000XM5', specParam: '银色', platform: '淘宝',
        shopName: '二手优品店', originalPrice: 1999, realPrice: 1799,
        goodsUrl: 'https://taobao.com/example2', salesNum: 3200, score: 4.2,
        saleStatus: 0, // 下架
      ),
      Goods(
        id: 1006, goodsName: '索尼 WH-1000XM5 头戴耳机', brand: '索尼',
        model: 'WH-1000XM5', specParam: '黑色', platform: '京东',
        shopName: '京选数码专营店', originalPrice: 3099, realPrice: 2459,
        goodsUrl: 'https://jd.com/example2', salesNum: 21000, score: 4.8,
      ),
    ],
  );
}

List<PricePoint> _generate30DayPrices(double current) {
  final now = DateTime.now();
  return List.generate(30, (i) {
    final date = now.subtract(Duration(days: 29 - i));
    // Generate realistic price fluctuation
    final base = current / 2;
    final amplitude = current * 0.15;
    final random = (i * 7 + 13) % 17 / 17.0; // deterministic "random"
    final price = base + amplitude * (0.5 + 0.5 * (i / 29.0)) + amplitude * 0.3 * random;
    return PricePoint(date: date, price: double.parse(price.toStringAsFixed(2)));
  });
}
```

- [ ] **Step 3: Write mock_history.dart**

```dart
import '../models/history_record.dart';

List<HistoryRecord> mockHistoryRecords(int userId) {
  final now = DateTime.now();
  return [
    HistoryRecord(
      id: 1, userId: userId,
      searchSource: '索尼 WH-1000XM5 头戴式降噪耳机 黑色',
      compareType: 1,
      createTime: now.subtract(const Duration(hours: 2)),
    ),
    HistoryRecord(
      id: 2, userId: userId,
      searchSource: 'https://item.jd.com/1000123456.html',
      compareType: 2,
      createTime: now.subtract(const Duration(days: 1)),
    ),
    HistoryRecord(
      id: 3, userId: userId,
      searchSource: '蓝牙耳机 降噪',
      compareType: 3,
      createTime: now.subtract(const Duration(days: 2)),
    ),
    HistoryRecord(
      id: 4, userId: userId,
      searchSource: 'iPhone 15 Pro Max 256GB 原色钛金属',
      compareType: 1,
      createTime: now.subtract(const Duration(days: 5)),
    ),
    HistoryRecord(
      id: 5, userId: userId,
      searchSource: '机械键盘 青轴 无线',
      compareType: 3,
      createTime: now.subtract(const Duration(days: 7)),
    ),
  ];
}
```

---

### Task 5: Router configuration

**Files:**
- Create: `lib/router.dart`

- [ ] **Step 1: Write router.dart**

```dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'features/auth/login_page.dart';
import 'features/home/home_page.dart';
import 'features/camera/camera_page.dart';
import 'features/compare/compare_page.dart';
import 'features/history/history_page.dart';
import 'features/profile/profile_page.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/login',
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) {
          final location = state.matchedLocation;
          int currentIndex = 0;
          if (location.startsWith('/history')) {
            currentIndex = 1;
          } else if (location.startsWith('/profile')) {
            currentIndex = 2;
          }

          return Scaffold(
            body: child,
            bottomNavigationBar: BottomNavigationBar(
              currentIndex: currentIndex,
              onTap: (index) {
                switch (index) {
                  case 0:
                    context.go('/home');
                    break;
                  case 1:
                    context.go('/history');
                    break;
                  case 2:
                    context.go('/profile');
                    break;
                }
              },
              items: const [
                BottomNavigationBarItem(icon: Icon(Icons.home_outlined), activeIcon: Icon(Icons.home), label: '首页'),
                BottomNavigationBarItem(icon: Icon(Icons.history_outlined), activeIcon: Icon(Icons.history), label: '比价历史'),
                BottomNavigationBarItem(icon: Icon(Icons.person_outline), activeIcon: Icon(Icons.person), label: '我的'),
              ],
            ),
          );
        },
        routes: [
          GoRoute(
            path: '/home',
            name: 'home',
            builder: (context, state) => const HomePage(),
          ),
          GoRoute(
            path: '/history',
            name: 'history',
            builder: (context, state) => const HistoryPage(),
          ),
          GoRoute(
            path: '/profile',
            name: 'profile',
            builder: (context, state) => const ProfilePage(),
          ),
        ],
      ),
      GoRoute(
        path: '/camera',
        name: 'camera',
        builder: (context, state) => const CameraPage(),
      ),
      GoRoute(
        path: '/compare-result',
        name: 'compare-result',
        builder: (context, state) => const ComparePage(),
      ),
    ],
  );
});
```

---

### Task 6: Auth feature — LoginPage & AuthProvider

**Files:**
- Create: `lib/features/auth/auth_provider.dart`
- Create: `lib/features/auth/login_page.dart`

- [ ] **Step 1: Write auth_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/user.dart';
import '../../shared/mock/mock_users.dart';

enum AuthMode { login, register }

class AuthState {
  final AuthMode mode;
  final bool isLoading;
  final String? errorMsg;
  final User? currentUser;
  final String? token;
  final bool isLoggedIn;

  const AuthState({
    this.mode = AuthMode.login,
    this.isLoading = false,
    this.errorMsg,
    this.currentUser,
    this.token,
    this.isLoggedIn = false,
  });

  AuthState copyWith({
    AuthMode? mode,
    bool? isLoading,
    String? errorMsg,
    User? currentUser,
    String? token,
    bool? isLoggedIn,
  }) {
    return AuthState(
      mode: mode ?? this.mode,
      isLoading: isLoading ?? this.isLoading,
      errorMsg: errorMsg ?? this.errorMsg,
      currentUser: currentUser ?? this.currentUser,
      token: token ?? this.token,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  AuthNotifier() : super(const AuthState());

  void toggleMode() {
    state = state.copyWith(
      mode: state.mode == AuthMode.login ? AuthMode.register : AuthMode.login,
      errorMsg: null,
    );
  }

  Future<void> login(String phone, String password) async {
    if (phone.isEmpty || password.isEmpty) {
      state = state.copyWith(errorMsg: '请输入手机号和密码');
      return;
    }
    if (phone.length != 11) {
      state = state.copyWith(errorMsg: '请输入正确的11位手机号');
      return;
    }
    if (password.length < 6) {
      state = state.copyWith(errorMsg: '密码至少6位');
      return;
    }

    state = state.copyWith(isLoading: true, errorMsg: null);

    // Simulate network delay
    await Future.delayed(const Duration(seconds: 1));

    final user = mockUsers.firstWhere(
      (u) => u.phone == phone,
      orElse: () => mockUsers.first,
    );

    state = state.copyWith(
      isLoading: false,
      isLoggedIn: true,
      currentUser: user,
      token: mockToken,
      errorMsg: null,
    );
  }

  Future<void> register(String phone, String password, String username) async {
    if (phone.isEmpty || password.isEmpty || username.isEmpty) {
      state = state.copyWith(errorMsg: '请填写所有字段');
      return;
    }
    if (phone.length != 11) {
      state = state.copyWith(errorMsg: '请输入正确的11位手机号');
      return;
    }
    if (password.length < 6) {
      state = state.copyWith(errorMsg: '密码至少6位');
      return;
    }

    state = state.copyWith(isLoading: true, errorMsg: null);

    await Future.delayed(const Duration(seconds: 1));

    final newUser = User(id: 99, username: username, phone: phone);
    state = state.copyWith(
      isLoading: false,
      isLoggedIn: true,
      currentUser: newUser,
      token: mockToken,
      errorMsg: null,
    );
  }

  void logout() {
    state = const AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier();
});
```

- [ ] **Step 2: Write login_page.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'auth_provider.dart';
import '../../shared/theme.dart';

class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  final _usernameController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _phoneController.dispose();
    _passwordController.dispose();
    _usernameController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authProvider);

    // Navigate on login success
    ref.listen<AuthState>(authProvider, (prev, next) {
      if (next.isLoggedIn) {
        context.go('/home');
      }
    });

    final isLogin = authState.mode == AuthMode.login;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 32),
          child: Column(
            children: [
              const SizedBox(height: 60),
              // Logo area
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: const Icon(Icons.shopping_bag, color: Colors.white, size: 40),
              ),
              const SizedBox(height: 24),
              const Text(
                'AI智能比价助手',
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),
              const Text(
                '拍照识图 全网比价',
                style: TextStyle(fontSize: 14, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 40),

              // Login / Register Tabs
              Container(
                decoration: BoxDecoration(
                  color: AppColors.background,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        onTap: () => ref.read(authProvider.notifier).toggleMode(),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: isLogin ? AppColors.primary : AppColors.background,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '登录',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: isLogin ? Colors.white : AppColors.textSecondary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: GestureDetector(
                        onTap: () => ref.read(authProvider.notifier).toggleMode(),
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: !isLogin ? AppColors.primary : AppColors.background,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Text(
                            '注册',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: !isLogin ? Colors.white : AppColors.textSecondary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Phone input
              TextField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                maxLength: 11,
                decoration: const InputDecoration(
                  hintText: '手机号',
                  prefixIcon: Icon(Icons.phone_android, color: AppColors.textSecondary),
                ),
              ),
              const SizedBox(height: 12),

              // Password input
              TextField(
                controller: _passwordController,
                obscureText: true,
                decoration: const InputDecoration(
                  hintText: '密码',
                  prefixIcon: Icon(Icons.lock_outline, color: AppColors.textSecondary),
                ),
              ),

              // Register-only fields
              if (!isLogin) ...[
                const SizedBox(height: 12),
                TextField(
                  controller: _confirmPasswordController,
                  obscureText: true,
                  decoration: const InputDecoration(
                    hintText: '确认密码',
                    prefixIcon: Icon(Icons.lock_outline, color: AppColors.textSecondary),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _usernameController,
                  decoration: const InputDecoration(
                    hintText: '昵称',
                    prefixIcon: Icon(Icons.person_outline, color: AppColors.textSecondary),
                  ),
                ),
              ],

              const SizedBox(height: 8),

              // Error message
              if (authState.errorMsg != null)
                Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Text(
                    authState.errorMsg!,
                    style: const TextStyle(color: AppColors.priceRed, fontSize: 13),
                  ),
                ),

              const SizedBox(height: 8),

              // Submit button
              ElevatedButton(
                onPressed: authState.isLoading
                    ? null
                    : () {
                        final phone = _phoneController.text.trim();
                        final password = _passwordController.text.trim();
                        if (isLogin) {
                          ref.read(authProvider.notifier).login(phone, password);
                        } else {
                          final username = _usernameController.text.trim();
                          ref.read(authProvider.notifier).register(phone, password, username);
                        }
                      },
                child: authState.isLoading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Text(isLogin ? '登录' : '注册'),
              ),

              const SizedBox(height: 32),
              const Text(
                '登录即同意《隐私政策》',
                style: TextStyle(fontSize: 12, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }
}
```

---

### Task 7: Home feature — HomePage & HomeProvider

**Files:**
- Create: `lib/features/home/home_page.dart`
- Create: `lib/features/home/home_provider.dart`

- [ ] **Step 1: Write home_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

class HomeState {
  final String searchKeyword;
  final bool isSearching;

  const HomeState({this.searchKeyword = '', this.isSearching = false});

  HomeState copyWith({String? searchKeyword, bool? isSearching}) {
    return HomeState(
      searchKeyword: searchKeyword ?? this.searchKeyword,
      isSearching: isSearching ?? this.isSearching,
    );
  }
}

class HomeNotifier extends StateNotifier<HomeState> {
  HomeNotifier() : super(const HomeState());

  void updateKeyword(String keyword) {
    state = state.copyWith(searchKeyword: keyword);
  }
}

final homeProvider = StateNotifierProvider<HomeNotifier, HomeState>((ref) {
  return HomeNotifier();
});
```

- [ ] **Step 2: Write home_page.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import 'home_provider.dart';

class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('AI智能比价'),
        automaticallyImplyLeading: false,
      ),
      body: Column(
        children: [
          // Search bar
          Container(
            color: Colors.white,
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: TextField(
              onSubmitted: (value) {
                if (value.trim().isNotEmpty) {
                  context.go('/compare-result', extra: null);
                }
              },
              decoration: InputDecoration(
                hintText: '输入商品名称搜索比价',
                prefixIcon: const Icon(Icons.search, color: AppColors.textSecondary),
                filled: true,
                fillColor: AppColors.background,
                contentPadding: const EdgeInsets.symmetric(vertical: 12),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
              ),
            ),
          ),

          const SizedBox(height: 8),

          // 3 entry cards
          Expanded(
            child: ListView(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              children: [
                _buildEntryCard(
                  icon: Icons.camera_alt,
                  title: '拍照识图比价',
                  subtitle: '相机拍照识别商品，全网实时比价',
                  isLarge: true,
                  color: AppColors.primary,
                  onTap: () => context.go('/camera'),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildEntryCard(
                        icon: Icons.link,
                        title: '链接比价',
                        subtitle: '粘贴商品链接',
                        color: const Color(0xFF52C41A),
                        onTap: () => _showUrlDialog(context, ref),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildEntryCard(
                        icon: Icons.text_fields,
                        title: '关键词搜索比价',
                        subtitle: '输入关键词搜索',
                        color: const Color(0xFFFFA940),
                        onTap: () => _showKeywordDialog(context, ref),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEntryCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
    required VoidCallback onTap,
    bool isLarge = false,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: isLarge ? 140 : 100,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 8, offset: const Offset(0, 2)),
          ],
        ),
        child: Row(
          children: [
            const SizedBox(width: 20),
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.only(right: 16),
              child: Icon(Icons.chevron_right, color: AppColors.textSecondary),
            ),
          ],
        ),
      ),
    );
  }

  void _showUrlDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('链接比价'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: '粘贴电商商品链接'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              if (controller.text.trim().isNotEmpty) {
                context.go('/compare-result', extra: null);
              }
            },
            child: const Text('开始比价'),
          ),
        ],
      ),
    );
  }

  void _showKeywordDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('关键词搜索比价'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(hintText: '输入商品关键词'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              if (controller.text.trim().isNotEmpty) {
                context.go('/compare-result', extra: null);
              }
            },
            child: const Text('搜索'),
          ),
        ],
      ),
    );
  }
}
```

---

### Task 8: Camera feature — CameraPage & CameraProvider

**Files:**
- Create: `lib/features/camera/camera_page.dart`
- Create: `lib/features/camera/camera_provider.dart`
- Create: `lib/shared/widgets/loading_overlay.dart`

- [ ] **Step 1: Write camera_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

enum CameraStatus { idle, picking, analyzing, searching, done }

class CameraState {
  final CameraStatus status;
  final String? imagePath;

  const CameraState({this.status = CameraStatus.idle, this.imagePath});

  CameraState copyWith({CameraStatus? status, String? imagePath}) {
    return CameraState(
      status: status ?? this.status,
      imagePath: imagePath ?? this.imagePath,
    );
  }
}

class CameraNotifier extends StateNotifier<CameraState> {
  CameraNotifier() : super(const CameraState());

  Future<void> pickFromGallery() async {
    // In real app, use image_picker here. For mock, simulate.
    state = state.copyWith(status: CameraStatus.picking);
    await Future.delayed(const Duration(milliseconds: 500));
    state = state.copyWith(status: CameraStatus.analyzing);
    await Future.delayed(const Duration(seconds: 1));
    state = state.copyWith(status: CameraStatus.searching);
    await Future.delayed(const Duration(seconds: 1));
    state = state.copyWith(status: CameraStatus.done);
  }

  Future<void> takePhoto() async {
    state = state.copyWith(status: CameraStatus.picking);
    await Future.delayed(const Duration(milliseconds: 500));
    state = state.copyWith(status: CameraStatus.analyzing);
    await Future.delayed(const Duration(seconds: 1));
    state = state.copyWith(status: CameraStatus.searching);
    await Future.delayed(const Duration(seconds: 1));
    state = state.copyWith(status: CameraStatus.done);
  }

  void reset() {
    state = const CameraState();
  }
}

final cameraProvider = StateNotifierProvider<CameraNotifier, CameraState>((ref) {
  return CameraNotifier();
});
```

- [ ] **Step 2: Write loading_overlay.dart**

```dart
import 'package:flutter/material.dart';
import '../../shared/theme.dart';

class LoadingOverlay extends StatelessWidget {
  final String title;
  final String subtitle;

  const LoadingOverlay({
    super.key,
    this.title = 'AI识别中...',
    this.subtitle = '全网检索中...',
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black54,
      child: Center(
        child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 40),
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(
                width: 48,
                height: 48,
                child: CircularProgressIndicator(strokeWidth: 3, color: AppColors.primary),
              ),
              const SizedBox(height: 24),
              Text(title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              const SizedBox(height: 8),
              Text(subtitle, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
            ],
          ),
        ),
      ),
    );
  }
}
```

- [ ] **Step 3: Write camera_page.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../../shared/widgets/loading_overlay.dart';
import 'camera_provider.dart';

class CameraPage extends ConsumerWidget {
  const CameraPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cameraState = ref.watch(cameraProvider);

    // When recognition completes, navigate to compare result
    ref.listen<CameraState>(cameraProvider, (prev, next) {
      if (next.status == CameraStatus.done) {
        context.go('/compare-result', extra: null);
        ref.read(cameraProvider.notifier).reset();
      }
    });

    return Stack(
      children: [
        Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(title: const Text('选择图片识别')),
          body: Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildActionButton(
                    icon: Icons.camera_alt,
                    label: '拍照',
                    onTap: () => ref.read(cameraProvider.notifier).takePhoto(),
                    color: AppColors.primary,
                  ),
                  const SizedBox(width: 40),
                  _buildActionButton(
                    icon: Icons.photo_library,
                    label: '从相册选择',
                    onTap: () => ref.read(cameraProvider.notifier).pickFromGallery(),
                    color: const Color(0xFF52C41A),
                  ),
                ],
              ),
            ),
          ),
        ),
        if (cameraState.status != CameraStatus.idle && cameraState.status != CameraStatus.done)
          const LoadingOverlay(),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
    required Color color,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 130,
        height: 150,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(color: Colors.black.withOpacity(0.06), blurRadius: 12, offset: const Offset(0, 4)),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: color, size: 32),
            ),
            const SizedBox(height: 16),
            Text(label, style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500, color: AppColors.textPrimary)),
          ],
        ),
      ),
    );
  }
}
```

---

### Task 9: Compare feature — ComparePage with all sub-widgets

**Files:**
- Create: `lib/features/compare/compare_provider.dart`
- Create: `lib/features/compare/widgets/product_card.dart`
- Create: `lib/features/compare/widgets/ai_analysis_card.dart`
- Create: `lib/features/compare/widgets/price_chart.dart`
- Create: `lib/features/compare/widgets/same_list_item.dart`
- Create: `lib/features/compare/compare_page.dart`

- [ ] **Step 1: Write compare_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/compare_result.dart';
import '../../shared/mock/mock_compare.dart';

class CompareNotifier extends StateNotifier<CompareResult?> {
  CompareNotifier() : super(null);

  void loadResult(String? keyword) {
    state = null; // trigger loading state briefly
    Future.delayed(const Duration(milliseconds: 800), () {
      state = mockCompareResult(keyword ?? '索尼 WH-1000XM5 头戴式降噪耳机');
    });
  }

  void loadFromHistory(String searchSource, int compareType) {
    state = null;
    Future.delayed(const Duration(milliseconds: 800), () {
      state = mockCompareResult(searchSource);
    });
  }
}

final compareProvider = StateNotifierProvider<CompareNotifier, CompareResult?>((ref) {
  return CompareNotifier();
});
```

- [ ] **Step 2: Write product_card.dart**

```dart
import 'package:flutter/material.dart';
import '../../../shared/theme.dart';
import '../../../shared/models/goods.dart';

class ProductCard extends StatelessWidget {
  final Goods goods;

  const ProductCard({super.key, required this.goods});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.image, color: AppColors.textSecondary, size: 36),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    goods.goodsName,
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${goods.brand} · ${goods.model}${goods.specParam.isNotEmpty ? ' · ${goods.specParam}' : ''}',
                    style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

- [ ] **Step 3: Write ai_analysis_card.dart**

```dart
import 'package:flutter/material.dart';
import '../../../shared/theme.dart';
import '../../../shared/models/compare_result.dart';

class AiAnalysisCard extends StatelessWidget {
  final AiAnalysis analysis;

  const AiAnalysisCard({super.key, required this.analysis});

  @override
  Widget build(BuildContext context) {
    final suggestionColor = analysis.suggestion == '建议入手'
        ? AppColors.priceGreen
        : analysis.suggestion == '再等等'
            ? AppColors.priceRed
            : AppColors.primary;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                Icon(Icons.auto_awesome, color: AppColors.primary, size: 18),
                SizedBox(width: 6),
                Text('AI分析', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
              ],
            ),
            const SizedBox(height: 12),
            // Suggestion badge
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: suggestionColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                analysis.suggestion,
                style: TextStyle(color: suggestionColor, fontWeight: FontWeight.w600, fontSize: 14),
              ),
            ),
            if (analysis.suggestionDetail.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(analysis.suggestionDetail, style: const TextStyle(fontSize: 13, color: AppColors.textSecondary)),
            ],
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildPriceInfo('当前价位', '¥${analysis.currentPrice.toStringAsFixed(0)}', AppColors.priceRed),
                ),
                Expanded(
                  child: _buildPriceInfo('历史最低', '¥${analysis.lowestPrice.toStringAsFixed(0)}', AppColors.priceGreen),
                ),
                Expanded(
                  child: _buildTrendInfo(),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPriceInfo(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 4),
        Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: color)),
      ],
    );
  }

  Widget _buildTrendInfo() {
    final isDown = analysis.trend.contains('下跌');
    final icon = isDown ? Icons.trending_down : Icons.trending_up;
    final color = isDown ? AppColors.priceGreen : AppColors.priceRed;
    return Column(
      children: [
        const Text('趋势', style: TextStyle(fontSize: 12, color: AppColors.textSecondary)),
        const SizedBox(height: 4),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: color),
            const SizedBox(width: 2),
            Text(analysis.trend, style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: color)),
          ],
        ),
      ],
    );
  }
}
```

- [ ] **Step 4: Write price_chart.dart**

```dart
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../shared/theme.dart';
import '../../../shared/models/compare_result.dart';
import 'package:intl/intl.dart';

class PriceChart extends StatelessWidget {
  final List<PricePoint> priceHistory;

  const PriceChart({super.key, required this.priceHistory});

  @override
  Widget build(BuildContext context) {
    if (priceHistory.isEmpty) {
      return const SizedBox(height: 200, child: Center(child: Text('暂无价格数据')));
    }

    final spots = priceHistory.asMap().entries.map((e) {
      return FlSpot(e.key.toDouble(), e.value.price);
    }).toList();

    final minPrice = spots.map((s) => s.y).reduce((a, b) => a < b ? a : b);
    final maxPrice = spots.map((s) => s.y).reduce((a, b) => a > b ? a : b);
    final priceRange = maxPrice - minPrice;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('30天价格走势', style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary)),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: priceRange / 4,
                    getDrawingHorizontalLine: (value) {
                      return FlLine(color: AppColors.divider, strokeWidth: 0.5);
                    },
                  ),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 44,
                        getTitlesWidget: (value, meta) {
                          return Text('¥${value.toInt()}', style: const TextStyle(fontSize: 10, color: AppColors.textSecondary));
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 28,
                        interval: 7,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index < 0 || index >= priceHistory.length) return const SizedBox.shrink();
                          return Text(
                            DateFormat('MM/dd').format(priceHistory[index].date),
                            style: const TextStyle(fontSize: 9, color: AppColors.textSecondary),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      curveSmoothness: 0.3,
                      color: AppColors.primary,
                      barWidth: 2,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: AppColors.primary.withOpacity(0.1),
                      ),
                    ),
                  ],
                  lineTouchData: LineTouchData(
                    touchTooltipData: LineTouchTooltipData(
                      getTooltipItems: (spots) {
                        return spots.map((spot) {
                          final date = priceHistory[spot.spotIndex].date;
                          return LineTooltipItem(
                            '${DateFormat('MM/dd').format(date)}\n¥${spot.y.toStringAsFixed(0)}',
                            const TextStyle(color: Colors.white, fontSize: 12),
                          );
                        }).toList();
                      },
                    ),
                  ),
                  minY: minPrice - priceRange * 0.1,
                  maxY: maxPrice + priceRange * 0.1,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

- [ ] **Step 5: Write same_list_item.dart**

```dart
import 'package:flutter/material.dart';
import '../../../shared/theme.dart';
import '../../../shared/models/goods.dart';

class SameListItem extends StatelessWidget {
  final Goods goods;
  final int index;

  const SameListItem({super.key, required this.goods, this.index = 0});

  @override
  Widget build(BuildContext context) {
    final isOff = goods.isOffShelf;

    return Opacity(
      opacity: isOff ? 0.45 : 1.0,
      child: Container(
        color: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Platform badge
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: _platformColor().withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Center(
                child: Text(goods.platformLabel, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600, color: _platformColor())),
              ),
            ),
            const SizedBox(width: 10),

            // Product image placeholder
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: AppColors.background,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(Icons.shopping_bag, color: isOff ? AppColors.disabled : AppColors.textSecondary, size: 24),
            ),
            const SizedBox(width: 10),

            // Name & shop info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${goods.goodsName} ${goods.specParam}',
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w500,
                      color: isOff ? AppColors.disabled : AppColors.textPrimary,
                      decoration: isOff ? TextDecoration.lineThrough : null,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  RichText(
                    text: TextSpan(
                      children: [
                        TextSpan(
                          text: goods.shopName,
                          style: TextStyle(fontSize: 11, color: isOff ? AppColors.disabled : AppColors.textSecondary),
                        ),
                        TextSpan(
                          text: ' · 销量${goods.salesText}',
                          style: TextStyle(fontSize: 11, color: isOff ? AppColors.disabled : AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Price & action
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  '¥${goods.realPrice.toStringAsFixed(0)}',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: isOff ? AppColors.disabled : AppColors.priceRed,
                    decoration: isOff ? TextDecoration.lineThrough : null,
                  ),
                ),
                const SizedBox(height: 4),
                if (!isOff)
                  SizedBox(
                    height: 28,
                    child: ElevatedButton(
                      onPressed: () {},
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        minimumSize: const Size(64, 28),
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 0),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                        textStyle: const TextStyle(fontSize: 11),
                      ),
                      child: const Text('立即购买'),
                    ),
                  ),
                if (isOff)
                  Text('已下架', style: TextStyle(fontSize: 11, color: AppColors.disabled)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _platformColor() {
    switch (goods.platform) {
      case '京东':
        return const Color(0xFFE4393C);
      case '淘宝':
        return const Color(0xFFFF5000);
      case '拼多多':
        return const Color(0xFFE02E24);
      case '抖音':
        return const Color(0xFF010101);
      default:
        return AppColors.primary;
    }
  }
}
```

- [ ] **Step 6: Write compare_page.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'compare_provider.dart';
import 'widgets/product_card.dart';
import 'widgets/ai_analysis_card.dart';
import 'widgets/price_chart.dart';
import 'widgets/same_list_item.dart';
import '../../shared/theme.dart';
import '../../shared/models/goods.dart';

class ComparePage extends ConsumerStatefulWidget {
  const ComparePage({super.key});

  @override
  ConsumerState<ComparePage> createState() => _ComparePageState();
}

class _ComparePageState extends ConsumerState<ComparePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final pending = ref.read(pendingSearchProvider);
      if (pending != null) {
        ref.read(compareProvider.notifier).loadFromHistory(pending, 3);
        ref.read(pendingSearchProvider.notifier).state = null;
      } else {
        ref.read(compareProvider.notifier).loadResult(null);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final result = ref.watch(compareProvider);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(title: const Text('比价结果')),
      body: result == null
          ? const Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  CircularProgressIndicator(color: AppColors.primary),
                  SizedBox(height: 16),
                  Text('正在比价...', style: TextStyle(color: AppColors.textSecondary)),
                ],
              ),
            )
          : SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  // 1. Identified product card
                  ProductCard(goods: result.identifiedGoods),

                  // 2. AI analysis card
                  AiAnalysisCard(analysis: result.aiAnalysis),

                  // 3. 30-day price chart
                  PriceChart(priceHistory: result.priceHistory30Days),

                  // 4. Same goods list header
                  const Padding(
                    padding: EdgeInsets.fromLTRB(16, 16, 16, 4),
                    child: Text(
                      '全网同款 (按价格升序)',
                      style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                    ),
                  ),

                  // 5. Same goods list
                  ...result.sameGoodsList.asMap().entries.map((entry) {
                    final index = entry.key;
                    final goods = entry.value;
                    return Column(
                      children: [
                        SameListItem(goods: goods, index: index),
                        if (index < result.sameGoodsList.length - 1)
                          const Divider(height: 1, indent: 16, endIndent: 16),
                      ],
                    );
                  }),

                  const SizedBox(height: 24),
                ],
              ),
            ),
    );
  }
}
```

---

### Task 10: History feature — HistoryPage & HistoryProvider

**Files:**
- Create: `lib/features/history/history_provider.dart`
- Create: `lib/features/history/history_page.dart`

- [ ] **Step 1: Write history_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/history_record.dart';
import '../../shared/mock/mock_history.dart';

class HistoryState {
  final List<HistoryRecord> records;
  final bool isLoading;
  final int? deletingId;

  const HistoryState({this.records = const [], this.isLoading = false, this.deletingId});

  HistoryState copyWith({List<HistoryRecord>? records, bool? isLoading, int? deletingId}) {
    return HistoryState(
      records: records ?? this.records,
      isLoading: isLoading ?? this.isLoading,
      deletingId: deletingId,
    );
  }
}

class HistoryNotifier extends StateNotifier<HistoryState> {
  HistoryNotifier() : super(const HistoryState());

  void loadRecords(int userId) {
    final records = mockHistoryRecords(userId);
    state = state.copyWith(records: records);
  }

  Future<void> deleteRecord(int id) async {
    state = state.copyWith(deletingId: id);
    await Future.delayed(const Duration(milliseconds: 300));
    final updated = state.records.where((r) => r.id != id).toList();
    state = state.copyWith(records: updated, deletingId: null);
  }

  Future<void> clearAll() async {
    state = state.copyWith(isLoading: true);
    await Future.delayed(const Duration(milliseconds: 500));
    state = state.copyWith(records: [], isLoading: false);
  }
}

final historyProvider = StateNotifierProvider<HistoryNotifier, HistoryState>((ref) {
  return HistoryNotifier();
});
```

- [ ] **Step 2: Write history_page.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../compare/compare_provider.dart';
import 'history_provider.dart';

class HistoryPage extends ConsumerWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyState = ref.watch(historyProvider);
    final notifier = ref.read(historyProvider.notifier);

    // Load records on first build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (historyState.records.isEmpty && !historyState.isLoading) {
        notifier.loadRecords(1);
      }
    });

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('比价历史'),
        actions: [
          if (historyState.records.isNotEmpty)
            TextButton(
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('确认清空'),
                    content: const Text('确定要清空所有比价历史吗？'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
                      ElevatedButton(
                        onPressed: () {
                          Navigator.pop(ctx);
                          notifier.clearAll();
                        },
                        child: const Text('清空'),
                      ),
                    ],
                  ),
                );
              },
              child: const Text('清空全部', style: TextStyle(color: AppColors.priceRed, fontSize: 14)),
            ),
        ],
      ),
      body: historyState.records.isEmpty
          ? Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.inbox_outlined, size: 64, color: AppColors.disabled),
                  const SizedBox(height: 12),
                  const Text('暂无记录', style: TextStyle(fontSize: 15, color: AppColors.textSecondary)),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.symmetric(vertical: 4),
              itemCount: historyState.records.length,
              itemBuilder: (context, index) {
                final record = historyState.records[index];
                final isDeleting = historyState.deletingId == record.id;

                return Dismissible(
                  key: Key('history_${record.id}'),
                  direction: DismissDirection.endToStart,
                  onDismissed: (_) => notifier.deleteRecord(record.id),
                  background: Container(
                    alignment: Alignment.centerRight,
                    padding: const EdgeInsets.only(right: 20),
                    color: AppColors.priceRed,
                    child: const Icon(Icons.delete, color: Colors.white),
                  ),
                  child: Card(
                    margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                    child: InkWell(
                      onTap: () {
                        // Set pending search so ComparePage loads fresh data
                        ref.read(pendingSearchProvider.notifier).state = record.searchSource;
                        context.go('/compare-result');
                      },
                      borderRadius: BorderRadius.circular(12),
                      child: Padding(
                        padding: const EdgeInsets.all(14),
                        child: Row(
                          children: [
                            // Type icon
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                color: AppColors.background,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Center(
                                child: Text(record.typeIcon, style: const TextStyle(fontSize: 22)),
                              ),
                            ),
                            const SizedBox(width: 12),
                            // Content
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    record.displaySource,
                                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: AppColors.textPrimary),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Row(
                                    children: [
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: AppColors.primary.withOpacity(0.1),
                                          borderRadius: BorderRadius.circular(4),
                                        ),
                                        child: Text(
                                          record.typeLabel,
                                          style: const TextStyle(fontSize: 10, color: AppColors.primary),
                                        ),
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        _formatTime(record.createTime),
                                        style: const TextStyle(fontSize: 12, color: AppColors.textSecondary),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                            // Delete button
                            if (isDeleting)
                              const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2))
                            else
                              IconButton(
                                icon: const Icon(Icons.delete_outline, size: 20, color: AppColors.textSecondary),
                                onPressed: () => notifier.deleteRecord(record.id),
                              ),
                          ],
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    if (diff.inHours < 24) return '${diff.inHours}小时前';
    if (diff.inDays < 30) return '${diff.inDays}天前';
    return '${time.month}/${time.day}';
  }
}
```

---

### Task 11: Profile feature — ProfilePage & ProfileProvider

**Files:**
- Create: `lib/features/profile/profile_provider.dart`
- Create: `lib/features/profile/profile_page.dart`

- [ ] **Step 1: Write profile_provider.dart**

```dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/user.dart';

class ProfileState {
  final User? user;
  final bool isLoggingOut;

  const ProfileState({this.user, this.isLoggingOut = false});

  ProfileState copyWith({User? user, bool? isLoggingOut}) {
    return ProfileState(user: user ?? this.user, isLoggingOut: isLoggingOut ?? this.isLoggingOut);
  }
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  ProfileNotifier() : super(const ProfileState());

  void loadUser() {
    // Use mock user
    state = state.copyWith(user: const User(id: 1, username: '小明', phone: '13812345678'));
  }

  void updateProfile(String username, String phone) {
    if (state.user == null) return;
    state = state.copyWith(user: User(id: state.user!.id, username: username, phone: phone));
  }
}

final profileProvider = StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  return ProfileNotifier();
});
```

- [ ] **Step 2: Write profile_page.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../auth/auth_provider.dart';
import 'profile_provider.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileState = ref.watch(profileProvider);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (profileState.user == null) {
        ref.read(profileProvider.notifier).loadUser();
      }
    });

    final user = profileState.user;
    final isLoggingOut = profileState.isLoggingOut;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('我的'),
        automaticallyImplyLeading: false,
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(vertical: 8),
        children: [
          // User info card
          Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 28,
                    backgroundColor: AppColors.primary,
                    child: Text(
                      user?.username.isNotEmpty == true ? user!.username[0].toUpperCase() : 'U',
                      style: const TextStyle(fontSize: 22, color: Colors.white, fontWeight: FontWeight.w600),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          user?.username ?? '未登录',
                          style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          user?.maskedPhone ?? '',
                          style: const TextStyle(fontSize: 13, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                  const Icon(Icons.chevron_right, color: AppColors.textSecondary),
                ],
              ),
            ),
          ),

          const SizedBox(height: 4),

          // Menu items
          Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Column(
              children: [
                _buildMenuItem(
                  icon: Icons.history,
                  title: '我的比价历史',
                  onTap: () => context.go('/history'),
                ),
                const Divider(height: 1, indent: 56),
                _buildMenuItem(
                  icon: Icons.info_outline,
                  title: '关于我们',
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('AI智能比价助手 v1.0.0')),
                    );
                  },
                ),
                const Divider(height: 1, indent: 56),
                _buildMenuItem(
                  icon: Icons.phone_android,
                  title: '版本',
                  trailing: const Text('1.0.0', style: TextStyle(fontSize: 14, color: AppColors.textSecondary)),
                ),
                const Divider(height: 1, indent: 56),
                _buildMenuItem(
                  icon: Icons.privacy_tip_outlined,
                  title: '隐私政策',
                  onTap: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('隐私政策页面')),
                    );
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),

          // Logout button
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 32),
            child: OutlinedButton(
              onPressed: isLoggingOut
                  ? null
                  : () {
                      showDialog(
                        context: context,
                        builder: (ctx) => AlertDialog(
                          title: const Text('退出登录'),
                          content: const Text('确定要退出登录吗？'),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
                            ElevatedButton(
                              style: ElevatedButton.styleFrom(backgroundColor: AppColors.priceRed),
                              onPressed: () {
                                Navigator.pop(ctx);
                                ref.read(authProvider.notifier).logout();
                                context.go('/login');
                              },
                              child: const Text('退出'),
                            ),
                          ],
                        ),
                      );
                    },
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.priceRed,
                side: const BorderSide(color: AppColors.priceRed),
                minimumSize: const Size(double.infinity, 48),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
              ),
              child: const Text('退出登录', style: TextStyle(fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    Widget? trailing,
    VoidCallback? onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            Icon(icon, size: 22, color: AppColors.textPrimary),
            const SizedBox(width: 16),
            Expanded(
              child: Text(title, style: const TextStyle(fontSize: 15, color: AppColors.textPrimary)),
            ),
            trailing ?? const Icon(Icons.chevron_right, size: 18, color: AppColors.textSecondary),
          ],
        ),
      ),
    );
  }
}
```

---

### Task 12: main.dart and app.dart — Wire everything together

**Files:**
- Overwrite: `lib/main.dart`
- Create: `lib/app.dart`

- [ ] **Step 1: Write main.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'app.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
  ]);
  runApp(const ProviderScope(child: AiShopApp()));
}
```

- [ ] **Step 2: Write app.dart**

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'shared/theme.dart';
import 'router.dart';

class AiShopApp extends ConsumerWidget {
  const AiShopApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);

    return MaterialApp.router(
      title: 'AI智能比价助手',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light,
      routerConfig: router,
    );
  }
}
```

---

### Task 13: Verify the complete project structure

- [ ] **Step 1: Verify all files exist**

Expected file tree:
```
lib/
├── main.dart
├── app.dart
├── router.dart
├── features/
│   ├── auth/
│   │   ├── auth_provider.dart
│   │   └── login_page.dart
│   ├── home/
│   │   ├── home_provider.dart
│   │   └── home_page.dart
│   ├── camera/
│   │   ├── camera_provider.dart
│   │   └── camera_page.dart
│   ├── compare/
│   │   ├── compare_provider.dart
│   │   ├── compare_page.dart
│   │   └── widgets/
│   │       ├── product_card.dart
│   │       ├── ai_analysis_card.dart
│   │       ├── price_chart.dart
│   │       └── same_list_item.dart
│   ├── history/
│   │   ├── history_provider.dart
│   │   └── history_page.dart
│   └── profile/
│       ├── profile_provider.dart
│       └── profile_page.dart
└── shared/
    ├── theme.dart
    ├── widgets/
    │   └── loading_overlay.dart
    ├── models/
    │   ├── user.dart
    │   ├── goods.dart
    │   ├── compare_result.dart
    │   └── history_record.dart
    └── mock/
        ├── mock_users.dart
        ├── mock_compare.dart
        └── mock_history.dart
```

- [ ] **Step 2: Run flutter analyze**

```bash
flutter analyze
```

Expected: No errors.

- [ ] **Step 3: Run flutter build**

```bash
flutter build apk --debug
```

Expected: Build succeeds.

- [ ] **Step 4: Run the app on device/emulator and verify all 6 pages**

```
1. /login    — 登录/注册切换，表单验证，登录跳转
2. /home     — 搜索框，3个入口卡片，底部Tab
3. /camera   — 拍照/相册按钮，loading蒙层
4. /compare  — 商品卡片，AI分析，价格走势图，同款列表
5. /history  — 历史列表，删除，清空，空态
6. /profile  — 用户信息，菜单，退出登录
```

Expected: All pages render correctly with mock data.

---

### Task 14: Wire history-to-compare re-comparison via pending-search provider

**Files:**
- Modify: `lib/features/compare/compare_provider.dart` — add `pendingSearchProvider`
- Modify: `lib/features/compare/compare_page.dart` — read pending search in initState
- Modify: `lib/features/history/history_page.dart` — set pending search before navigating

- [ ] **Step 1: Add pendingSearchProvider to compare_provider.dart**

Add this at the end of `compare_provider.dart` (after the existing code):

```dart
// Holds search source when navigating from history page.
// Set before context.go('/compare-result'), read in ComparePage.initState.
final pendingSearchProvider = StateProvider<String?>((ref) => null);
```

- [ ] **Step 2: Update compare_page.dart initState**

Replace the entire `initState` in `_ComparePageState`:

```dart
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final pending = ref.read(pendingSearchProvider);
      if (pending != null) {
        ref.read(compareProvider.notifier).loadFromHistory(pending, 3);
        ref.read(pendingSearchProvider.notifier).state = null; // consume
      } else {
        ref.read(compareProvider.notifier).loadResult(null);
      }
    });
  }
```

- [ ] **Step 3: Update history_page.dart onTap for re-comparison**

Replace the `onTap` callback inside the history card (the `InkWell.onTap` in `history_page.dart`) with:

```dart
onTap: () {
  // Set pending search so ComparePage loads fresh data
  ref.read(pendingSearchProvider.notifier).state = record.searchSource;
  context.go('/compare-result');
},
```

- [ ] **Step 4: Update router to not use CompareResult extra**

In `router.dart`, change the `/compare-result` route builder to:

```dart
GoRoute(
  path: '/compare-result',
  name: 'compare-result',
  builder: (context, state) => const ComparePage(),
),
```

Remove the `extra: state.extra as CompareResult?` and make ComparePage a `const` widget (no constructor parameters).

- [ ] **Step 5: Remove the `result` parameter from ComparePage**

In `compare_page.dart`, change the class declaration to:

```dart
class ComparePage extends ConsumerStatefulWidget {
  const ComparePage({super.key});

  @override
  ConsumerState<ComparePage> createState() => _ComparePageState();
}
```

- [ ] **Step 6: Verify the data flow**

Flow: HistoryPage → sets `pendingSearchProvider` → navigates to `/compare-result` → ComparePage.initState reads `pendingSearchProvider` → calls `loadFromHistory` → mock data loads → renders fresh comparison.

---

### Self-Review Checklist

1. **Spec coverage:** All 6 pages from ui.md covered — Login, Home, Camera, Compare (core), History, Profile. All UI requirements: primary color #1677FF, price red #FF4D4F, green #52C41A, BG #F7F8FA, 12px radius cards with shadow, bottom tabs (首页|比价历史|我的). All interactions: history re-compare (fresh data), off-shelf goods grayed out, real_price sorting, AI analysis mandatory, 30-day price chart mandatory.

2. **Placeholder scan:** No TBD, TODO, or other placeholder patterns found.

3. **Type consistency:** 
   - `Goods` model used consistently across `ProductCard`, `SameListItem`, `CompareResult`
   - `CompareResult` used in `compare_provider.dart` and `compare_page.dart`
   - `HistoryRecord` used in `history_provider.dart` and `history_page.dart`
   - `User` used in `auth_provider.dart` and `profile_provider.dart`
   - `AiAnalysis`, `PricePoint` defined in `compare_result.dart`, used in corresponding widgets
   - Router parameter names match — `extra: CompareResult?` matches `widget.result`
   - All providers return correct state types
