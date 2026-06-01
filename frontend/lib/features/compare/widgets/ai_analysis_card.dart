import 'package:flutter/material.dart';
import '../../../shared/models/compare_result.dart';
import '../../../shared/models/goods.dart';
import '../../../shared/theme.dart';
import '../../../shared/widgets/app_ui.dart';

class AiAnalysisCard extends StatelessWidget {
  final AiAnalysis analysis;
  final String goodsInfo;
  final List<Goods> compareList;

  const AiAnalysisCard({
    super.key,
    required this.analysis,
    required this.goodsInfo,
    required this.compareList,
  });

  @override
  Widget build(BuildContext context) {
    final levelColor = _priceLevelColor(analysis.priceLevel);
    final realPrices =
        compareList.where((g) => g.isOnSale).map((g) => g.realPrice).toList();
    final minPrice =
        realPrices.isEmpty ? 0.0 : realPrices.reduce((a, b) => a < b ? a : b);
    final maxPrice =
        realPrices.isEmpty ? 0.0 : realPrices.reduce((a, b) => a > b ? a : b);
    final avgPrice = realPrices.isEmpty
        ? 0.0
        : realPrices.reduce((a, b) => a + b) / realPrices.length;
    final highTrustCount = compareList.where((g) => g.trustScore >= 70).length;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: AppSurface(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Row(
              children: [
                AppIconBox(
                  icon: Icons.auto_awesome,
                  color: AppColors.primary,
                  size: 34,
                ),
                SizedBox(width: 8),
                Text('AI 分析',
                    style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary)),
              ],
            ),
            const SizedBox(height: 12),
            if (analysis.priceLevel.isNotEmpty)
              Container(
                margin: const EdgeInsets.only(bottom: 10),
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: levelColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  '价位 ${analysis.priceLevel}',
                  style: TextStyle(
                      color: levelColor,
                      fontWeight: FontWeight.w600,
                      fontSize: 14),
                ),
              ),
            if (realPrices.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Row(
                  children: [
                    _priceStat(
                        '当前最低', '¥${minPrice.toInt()}', AppColors.priceRed),
                    Container(width: 1, height: 28, color: AppColors.divider),
                    _priceStat(
                        '市场均价', '¥${avgPrice.toInt()}', AppColors.textPrimary),
                    Container(width: 1, height: 28, color: AppColors.divider),
                    _priceStat('高可信数', '$highTrustCount', AppColors.primary),
                    Container(width: 1, height: 28, color: AppColors.divider),
                    _priceStat(
                        '全网最高', '¥${maxPrice.toInt()}', AppColors.primary),
                  ],
                ),
              ),
            if (analysis.buyAdvice.isNotEmpty)
              _analysisLine(Icons.tips_and_updates, AppColors.priceGreen,
                  analysis.buyAdvice),
            if (analysis.pricePrediction.isNotEmpty)
              _analysisLine(Icons.trending_up, AppColors.priceRed,
                  analysis.pricePrediction),
          ],
        ),
      ),
    );
  }

  Widget _analysisLine(IconData icon, Color color, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(top: 2),
            child: Icon(icon, size: 16, color: color),
          ),
          const SizedBox(width: 6),
          Expanded(
              child: Text(text,
                  style: const TextStyle(
                      fontSize: 13, color: AppColors.textSecondary))),
        ],
      ),
    );
  }

  Widget _priceStat(String label, String value, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(label,
              style:
                  const TextStyle(fontSize: 11, color: AppColors.textSecondary),
              maxLines: 1),
          const SizedBox(height: 4),
          Text(value,
              style: TextStyle(
                  fontSize: 16, fontWeight: FontWeight.bold, color: color),
              maxLines: 1),
        ],
      ),
    );
  }

  Color _priceLevelColor(String level) {
    switch (level) {
      case '偏高':
        return AppColors.priceRed;
      case '偏低':
        return AppColors.priceGreen;
      default:
        return AppColors.primary;
    }
  }
}
