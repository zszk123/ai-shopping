import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../shared/theme.dart';
import '../../shared/widgets/app_ui.dart';
import '../compare/compare_provider.dart';

class HomePage extends ConsumerWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.only(bottom: 22),
          children: [
            const _HomeHeader(),
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 0),
              child: _SearchBox(
                onSubmit: (keyword) {
                  ref.read(compareProvider.notifier).compareByKeyword(keyword);
                  context.go('/compare-result');
                },
              ),
            ),
            const AppSectionTitle(
              title: '选择比价方式',
              subtitle: '图片、链接、关键词三种入口都可以继续全网比价',
            ),
            _CompareEntry(
              icon: Icons.camera_alt_outlined,
              title: '图片比价',
              subtitle: '拍照或从相册选择商品图，AI 识别后自动匹配同款',
              badge: '推荐',
              color: AppColors.primary,
              onTap: () => context.go('/camera'),
            ),
            _CompareEntry(
              icon: Icons.link,
              title: '链接比价',
              subtitle: '粘贴电商商品链接，直接分析同款和价格区间',
              badge: '更准确',
              color: AppColors.accent,
              onTap: () => _showUrlDialog(context, ref),
            ),
            _CompareEntry(
              icon: Icons.manage_search,
              title: '关键词比价',
              subtitle: '输入商品名、品牌、型号，适合图片识别失败后兜底',
              badge: '兜底',
              color: AppColors.warning,
              onTap: () => _showKeywordDialog(context, ref),
            ),
            const AppSectionTitle(title: '服务能力'),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Expanded(
                    child: _MetricCard(label: '同款识别', value: 'AI'),
                  ),
                  SizedBox(width: 10),
                  Expanded(
                    child: _MetricCard(label: '价格趋势', value: '30天'),
                  ),
                  SizedBox(width: 10),
                  Expanded(
                    child: _MetricCard(label: '购买建议', value: '智能'),
                  ),
                ],
              ),
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
          autofocus: true,
          decoration: const InputDecoration(hintText: '粘贴淘宝、京东等商品链接'),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () {
              final url = controller.text.trim();
              Navigator.pop(ctx);
              if (url.isNotEmpty) {
                ref.read(compareProvider.notifier).compareByUrl(url);
                context.go('/compare-result');
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
        title: const Text('关键词比价'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: '例如：iPhone 16 Pro 256GB'),
          onSubmitted: (_) => _submitKeyword(ctx, controller, ref, context),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: const Text('取消')),
          ElevatedButton(
            onPressed: () => _submitKeyword(ctx, controller, ref, context),
            child: const Text('搜索'),
          ),
        ],
      ),
    );
  }

  void _submitKeyword(
    BuildContext dialogContext,
    TextEditingController controller,
    WidgetRef ref,
    BuildContext pageContext,
  ) {
    final keyword = controller.text.trim();
    if (keyword.isEmpty) return;
    Navigator.pop(dialogContext);
    ref.read(compareProvider.notifier).compareByKeyword(keyword);
    pageContext.go('/compare-result');
  }
}

class _HomeHeader extends StatelessWidget {
  const _HomeHeader();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 14, 16, 0),
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: AppColors.primaryDark,
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Row(
        children: [
          AppIconBox(icon: Icons.bolt, color: AppColors.accent, size: 50),
          SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'AI 智能比价',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                SizedBox(height: 6),
                Text(
                  '识别同款、追踪历史价、给出更稳的购买建议',
                  style: TextStyle(color: Color(0xFFCBD5E1), fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _SearchBox extends StatelessWidget {
  final ValueChanged<String> onSubmit;

  const _SearchBox({required this.onSubmit});

  @override
  Widget build(BuildContext context) {
    final controller = TextEditingController();
    return TextField(
      controller: controller,
      textInputAction: TextInputAction.search,
      onSubmitted: (value) {
        final keyword = value.trim();
        if (keyword.isNotEmpty) onSubmit(keyword);
      },
      decoration: InputDecoration(
        hintText: '输入商品名称、品牌或型号',
        prefixIcon: const Icon(Icons.search, color: AppColors.textSecondary),
        suffixIcon: IconButton(
          tooltip: '搜索',
          icon: const Icon(Icons.arrow_forward),
          onPressed: () {
            final keyword = controller.text.trim();
            if (keyword.isNotEmpty) onSubmit(keyword);
          },
        ),
      ),
    );
  }
}

class _CompareEntry extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final String badge;
  final Color color;
  final VoidCallback onTap;

  const _CompareEntry({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.badge,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
      child: AppSurface(
        padding: EdgeInsets.zero,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(8),
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Row(
              children: [
                AppIconBox(icon: icon, color: color, size: 52),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Flexible(
                            child: Text(
                              title,
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w800,
                                color: AppColors.textPrimary,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          AppPill(text: badge, color: color),
                        ],
                      ),
                      const SizedBox(height: 5),
                      Text(
                        subtitle,
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                          fontSize: 12,
                          height: 1.4,
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: AppColors.textMuted),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String label;
  final String value;

  const _MetricCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return AppSurface(
      padding: const EdgeInsets.symmetric(vertical: 14),
      child: Column(
        children: [
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w900,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: 4),
          Text(label,
              style: const TextStyle(
                  fontSize: 12, color: AppColors.textSecondary)),
        ],
      ),
    );
  }
}
