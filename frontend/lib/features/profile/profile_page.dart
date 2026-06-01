import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../../shared/widgets/app_ui.dart';
import '../auth/auth_provider.dart';
import 'profile_provider.dart';

class ProfilePage extends ConsumerWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profileState = ref.watch(profileProvider);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!profileState.hasAttempted && !profileState.isLoading) {
        ref.read(profileProvider.notifier).loadUser();
      }
    });

    final user = profileState.user;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('我的'),
        automaticallyImplyLeading: false,
      ),
      body: profileState.isLoading
          ? const Center(
              child: CircularProgressIndicator(color: AppColors.primary))
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 28),
              children: [
                AppSurface(
                  padding: const EdgeInsets.all(16),
                  child: Row(
                    children: [
                      CircleAvatar(
                        radius: 28,
                        backgroundColor: AppColors.primaryDark,
                        child: Text(
                          user?.username.isNotEmpty == true
                              ? user!.username[0].toUpperCase()
                              : 'U',
                          style: const TextStyle(
                              fontSize: 22,
                              color: Colors.white,
                              fontWeight: FontWeight.w600),
                        ),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              user?.username ?? '未登录',
                              style: const TextStyle(
                                  fontSize: 17,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.textPrimary),
                            ),
                            const SizedBox(height: 4),
                            Text(
                              user?.maskedPhone ?? '',
                              style: const TextStyle(
                                  fontSize: 13, color: AppColors.textSecondary),
                            ),
                          ],
                        ),
                      ),
                      const AppPill(text: '已登录', color: AppColors.accent),
                    ],
                  ),
                ),
                const SizedBox(height: 12),
                AppSurface(
                  padding: EdgeInsets.zero,
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
                        trailing: const Text('1.0.0',
                            style: TextStyle(
                                fontSize: 14, color: AppColors.textSecondary)),
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
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  onPressed: profileState.isSaving
                      ? null
                      : () {
                          showDialog(
                            context: context,
                            builder: (ctx) => AlertDialog(
                              title: const Text('退出登录'),
                              content: const Text('确定要退出登录吗？'),
                              actions: [
                                TextButton(
                                    onPressed: () => Navigator.pop(ctx),
                                    child: const Text('取消')),
                                ElevatedButton(
                                  style: ElevatedButton.styleFrom(
                                      backgroundColor: AppColors.priceRed),
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
                  ),
                  icon: const Icon(Icons.logout),
                  label: const Text('退出登录'),
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
              child: Text(title,
                  style: const TextStyle(
                      fontSize: 15, color: AppColors.textPrimary)),
            ),
            trailing ??
                const Icon(Icons.chevron_right,
                    size: 18, color: AppColors.textSecondary),
          ],
        ),
      ),
    );
  }
}
