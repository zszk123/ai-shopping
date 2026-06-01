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
