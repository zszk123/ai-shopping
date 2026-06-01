import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../../shared/widgets/app_ui.dart';
import '../compare/compare_provider.dart';
import 'history_provider.dart';

class HistoryPage extends ConsumerWidget {
  const HistoryPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyState = ref.watch(historyProvider);

    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!historyState.hasAttempted && !historyState.isLoading) {
        ref.read(historyProvider.notifier).loadRecords();
      }
    });

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('比价历史'),
        automaticallyImplyLeading: false,
      ),
      body: _buildBody(context, ref, historyState),
    );
  }

  Widget _buildBody(BuildContext context, WidgetRef ref, HistoryState state) {
    if (state.isLoading && state.records.isEmpty) {
      return const Center(
          child: CircularProgressIndicator(color: AppColors.primary));
    }

    if (state.errorMsg != null && state.records.isEmpty) {
      return AppEmptyState(
        icon: Icons.cloud_off,
        title: '历史记录加载失败',
        message: state.errorMsg!,
        primaryText: '重试',
        onPrimary: () => ref.read(historyProvider.notifier).loadRecords(),
      );
    }

    if (state.records.isEmpty) {
      return AppEmptyState(
        icon: Icons.history,
        title: '暂无比价历史',
        message: '发起图片、链接或关键词比价后，这里会自动保存记录。',
        primaryText: '去比价',
        onPrimary: () => context.go('/home'),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 20),
      itemCount: state.records.length,
      itemBuilder: (context, index) {
        final record = state.records[index];
        final isDeleting = state.deletingId == record.id;

        return Dismissible(
          key: Key('history_${record.id}'),
          direction: DismissDirection.endToStart,
          onDismissed: (_) =>
              ref.read(historyProvider.notifier).deleteRecord(record.id),
          background: Container(
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 20),
            color: AppColors.priceRed,
            child: const Icon(Icons.delete, color: Colors.white),
          ),
          child: AppSurface(
            padding: EdgeInsets.zero,
            margin: const EdgeInsets.only(bottom: 10),
            child: InkWell(
              onTap: () {
                final ctx = SearchContext(
                  compareType: record.compareType,
                  searchSource: record.searchSource,
                );
                ref.read(compareProvider.notifier).loadFromContext(ctx);
                context.go('/compare-result');
              },
              borderRadius: BorderRadius.circular(8),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Row(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: AppColors.background,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: Center(
                        child: Icon(_recordIcon(record.compareType),
                            color: AppColors.primary, size: 24),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            record.displaySource,
                            style: const TextStyle(
                                fontSize: 14,
                                fontWeight: FontWeight.w500,
                                color: AppColors.textPrimary),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color:
                                      AppColors.primary.withValues(alpha: 0.1),
                                  borderRadius: BorderRadius.circular(4),
                                ),
                                child: Text(
                                  record.typeLabel,
                                  style: const TextStyle(
                                      fontSize: 10, color: AppColors.primary),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                _formatTime(record.createTime),
                                style: const TextStyle(
                                    fontSize: 12,
                                    color: AppColors.textSecondary),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    if (isDeleting)
                      const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2))
                    else
                      IconButton(
                        icon: const Icon(Icons.delete_outline,
                            size: 20, color: AppColors.textSecondary),
                        onPressed: () => ref
                            .read(historyProvider.notifier)
                            .deleteRecord(record.id),
                      ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }

  IconData _recordIcon(int type) {
    switch (type) {
      case 1:
        return Icons.image_search;
      case 2:
        return Icons.link;
      case 3:
        return Icons.manage_search;
      default:
        return Icons.receipt_long;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);
    if (diff.inHours < 24) return '${diff.inHours}小时前';
    if (diff.inDays < 30) return '${diff.inDays}天前';
    return '${time.month}/${time.day}';
  }
}
