import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/theme.dart';
import '../../shared/widgets/app_ui.dart';
import 'auth_provider.dart';

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
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(authProvider.notifier).tryAutoLogin();
    });
  }

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
    final isLogin = authState.mode == AuthMode.login;

    ref.listen<AuthState>(authProvider, (prev, next) {
      if (next.isLoggedIn) context.go('/home');
    });

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 460),
            child: ListView(
              padding: const EdgeInsets.fromLTRB(22, 26, 22, 22),
              children: [
                Row(
                  children: [
                    const AppIconBox(
                      icon: Icons.shopping_bag_outlined,
                      color: AppColors.primary,
                      size: 54,
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'AI 智能比价助手',
                            style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.w900,
                              color: AppColors.textPrimary,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            isLogin ? '登录后使用图片、链接、关键词比价' : '创建账号后开始使用全功能',
                            style: const TextStyle(
                              fontSize: 13,
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 28),
                AppSurface(
                  padding: const EdgeInsets.all(6),
                  color: AppColors.surfaceMuted,
                  child: Row(
                    children: [
                      _ModeTab(
                        label: '登录',
                        selected: isLogin,
                        onTap: () {
                          if (!isLogin) {
                            ref.read(authProvider.notifier).toggleMode();
                          }
                        },
                      ),
                      _ModeTab(
                        label: '注册',
                        selected: !isLogin,
                        onTap: () {
                          if (isLogin) {
                            ref.read(authProvider.notifier).toggleMode();
                          }
                        },
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 14),
                AppSurface(
                  padding: const EdgeInsets.all(18),
                  child: Column(
                    children: [
                      TextField(
                        controller: _phoneController,
                        keyboardType: TextInputType.phone,
                        maxLength: 11,
                        decoration: const InputDecoration(
                          counterText: '',
                          labelText: '手机号',
                          hintText: '请输入 11 位手机号',
                          prefixIcon: Icon(Icons.phone_android),
                        ),
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _passwordController,
                        obscureText: true,
                        decoration: const InputDecoration(
                          labelText: '密码',
                          hintText: '至少 6 位',
                          prefixIcon: Icon(Icons.lock_outline),
                        ),
                      ),
                      if (!isLogin) ...[
                        const SizedBox(height: 12),
                        TextField(
                          controller: _confirmPasswordController,
                          obscureText: true,
                          decoration: const InputDecoration(
                            labelText: '确认密码',
                            prefixIcon: Icon(Icons.lock_outline),
                          ),
                        ),
                        const SizedBox(height: 12),
                        TextField(
                          controller: _usernameController,
                          decoration: const InputDecoration(
                            labelText: '昵称',
                            hintText: '用于历史记录和客服识别',
                            prefixIcon: Icon(Icons.person_outline),
                          ),
                        ),
                      ],
                      if (authState.errorMsg != null) ...[
                        const SizedBox(height: 12),
                        AppSurface(
                          padding: const EdgeInsets.all(12),
                          color: const Color(0xFFFEF2F2),
                          child: Row(
                            children: [
                              const Icon(Icons.error_outline,
                                  size: 18, color: AppColors.priceRed),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  authState.errorMsg!,
                                  style: const TextStyle(
                                      color: AppColors.priceRed, fontSize: 13),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                      const SizedBox(height: 18),
                      ElevatedButton.icon(
                        onPressed:
                            authState.isLoading ? null : () => _submit(isLogin),
                        icon: authState.isLoading
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(
                                  strokeWidth: 2,
                                  color: Colors.white,
                                ),
                              )
                            : Icon(
                                isLogin ? Icons.login : Icons.person_add_alt_1),
                        label: Text(isLogin ? '登录并进入系统' : '注册并进入系统'),
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        '所有核心功能均需登录后使用',
                        style: TextStyle(
                          fontSize: 12,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 18),
                const _ValueGrid(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _submit(bool isLogin) {
    final phone = _phoneController.text.trim();
    final password = _passwordController.text.trim();
    if (isLogin) {
      ref.read(authProvider.notifier).login(phone, password);
      return;
    }
    final confirmPassword = _confirmPasswordController.text.trim();
    if (password != confirmPassword) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('两次输入的密码不一致')),
      );
      return;
    }
    final username = _usernameController.text.trim();
    ref.read(authProvider.notifier).register(phone, password, username);
  }
}

class _ModeTab extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _ModeTab({
    required this.label,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.symmetric(vertical: 11),
          decoration: BoxDecoration(
            color: selected ? Colors.white : Colors.transparent,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            label,
            textAlign: TextAlign.center,
            style: TextStyle(
              fontWeight: FontWeight.w800,
              color: selected ? AppColors.primary : AppColors.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}

class _ValueGrid extends StatelessWidget {
  const _ValueGrid();

  @override
  Widget build(BuildContext context) {
    return const Row(
      children: [
        Expanded(
          child: AppSurface(
            child: _ValueItem(
              icon: Icons.image_search,
              title: '图片识别',
              desc: '自动提取商品信息',
            ),
          ),
        ),
        SizedBox(width: 10),
        Expanded(
          child: AppSurface(
            child: _ValueItem(
              icon: Icons.verified_user_outlined,
              title: '可信排序',
              desc: '价格与店铺综合判断',
            ),
          ),
        ),
      ],
    );
  }
}

class _ValueItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final String desc;

  const _ValueItem({
    required this.icon,
    required this.title,
    required this.desc,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        AppIconBox(icon: icon, size: 38, color: AppColors.accent),
        const SizedBox(height: 10),
        Text(title,
            style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.w800,
                color: AppColors.textPrimary)),
        const SizedBox(height: 3),
        Text(desc,
            style:
                const TextStyle(fontSize: 12, color: AppColors.textSecondary)),
      ],
    );
  }
}
