import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../shared/theme.dart';
import '../../shared/widgets/loading_overlay.dart';
import '../../shared/widgets/app_ui.dart';
import '../compare/compare_provider.dart';
import 'camera_provider.dart';

class CameraPage extends ConsumerWidget {
  const CameraPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final cameraState = ref.watch(cameraProvider);
    final isPicking = cameraState.status == CameraStatus.picking;

    if (cameraState.status == CameraStatus.idle &&
        ModalRoute.of(context)?.isCurrent == true) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (!context.mounted) return;
        ref.read(compareProvider.notifier).reset();
        ref.read(pendingSearchProvider.notifier).state = null;
      });
    }

    ref.listen<CameraState>(cameraProvider, (prev, next) {
      if (next.status == CameraStatus.done && next.imageBytes != null) {
        ref.read(compareProvider.notifier).compareByImage(next.imageBytes!);
        context.go('/compare-result');
      }
    });

    return Stack(
      children: [
        Scaffold(
          backgroundColor: AppColors.background,
          appBar: AppBar(title: const Text('选择图片识别')),
          body: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const AppSurface(
                padding: EdgeInsets.all(18),
                color: AppColors.primaryDark,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    AppIconBox(
                      icon: Icons.image_search,
                      color: AppColors.accent,
                      size: 54,
                    ),
                    SizedBox(height: 14),
                    Text(
                      '上传清晰商品图',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      '尽量让商品主体、品牌、型号或包装文字出现在画面中，识别会更稳定。',
                      style: TextStyle(color: Color(0xFFCBD5E1), height: 1.45),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),
              _buildActionButton(
                icon: Icons.camera_alt_outlined,
                label: '拍照识别',
                subtitle: '适合线下门店、包装盒、商品铭牌',
                onTap: isPicking
                    ? null
                    : () => ref.read(cameraProvider.notifier).takePhoto(),
                color: AppColors.primary,
              ),
              const SizedBox(height: 10),
              _buildActionButton(
                icon: Icons.photo_library_outlined,
                label: '从相册选择',
                subtitle: '适合截图、商品详情页、已有图片',
                onTap: isPicking
                    ? null
                    : () => ref.read(cameraProvider.notifier).pickFromGallery(),
                color: AppColors.accent,
              ),
            ],
          ),
        ),
        if (cameraState.status != CameraStatus.idle &&
            cameraState.status != CameraStatus.done)
          const LoadingOverlay(
            title: '处理图片...',
            subtitle: '正在读取并压缩图片',
          ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required String subtitle,
    required VoidCallback? onTap,
    required Color color,
  }) {
    final enabled = onTap != null;
    return AppSurface(
      padding: EdgeInsets.zero,
      color: enabled ? Colors.white : const Color(0xFFF8FAFC),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              AppIconBox(
                icon: icon,
                color: enabled ? color : AppColors.disabled,
                size: 52,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(label,
                        style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            color: enabled
                                ? AppColors.textPrimary
                                : AppColors.textSecondary)),
                    const SizedBox(height: 5),
                    Text(subtitle,
                        style: const TextStyle(
                            fontSize: 12, color: AppColors.textSecondary)),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppColors.textMuted),
            ],
          ),
        ),
      ),
    );
  }
}
