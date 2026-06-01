import 'package:flutter/material.dart';
import '../../../shared/theme.dart';
import '../../../shared/widgets/app_ui.dart';

class ProductCard extends StatelessWidget {
  final String goodsInfo;

  const ProductCard({super.key, required this.goodsInfo});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: AppSurface(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const AppIconBox(
              icon: Icons.image_search,
              color: AppColors.primary,
              size: 64,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    goodsInfo.isEmpty ? '待识别商品' : goodsInfo,
                    style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    '已完成商品识别，将基于同款匹配、价格和店铺可信度综合排序。',
                    style:
                        TextStyle(fontSize: 13, color: AppColors.textSecondary),
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
