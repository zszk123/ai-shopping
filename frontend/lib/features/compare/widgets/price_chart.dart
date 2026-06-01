import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../shared/models/compare_result.dart';
import '../../../shared/theme.dart';
import '../../../shared/widgets/app_ui.dart';

class PriceChart extends StatelessWidget {
  final List<PricePoint> priceHistory;

  const PriceChart({super.key, required this.priceHistory});

  static List<PricePoint> _aggregateByDay(List<PricePoint> raw) {
    if (raw.isEmpty) return [];
    final map = <String, PricePoint>{};
    for (final p in raw) {
      final key = DateFormat('yyyy-MM-dd').format(p.date);
      final existing = map[key];
      if (existing == null || p.price < existing.price) {
        map[key] = p;
      }
    }
    final sorted = map.values.toList()
      ..sort((a, b) => a.date.compareTo(b.date));
    return sorted;
  }

  @override
  Widget build(BuildContext context) {
    final aggregated = _aggregateByDay(priceHistory);
    final spots = aggregated
        .asMap()
        .entries
        .map((e) => FlSpot(e.key.toDouble(), e.value.price))
        .toList();

    if (spots.isEmpty) {
      return _buildEmptyChart();
    }

    final minPrice = spots.map((s) => s.y).reduce((a, b) => a < b ? a : b);
    final maxPrice = spots.map((s) => s.y).reduce((a, b) => a > b ? a : b);
    final rawRange = maxPrice - minPrice;
    final priceRange =
        rawRange == 0 ? (maxPrice == 0 ? 100 : maxPrice * 0.5) : rawRange;
    final isSinglePoint = spots.length == 1;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: AppSurface(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('30 天价格走势',
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary)),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                LineChartData(
                  gridData: FlGridData(
                    show: true,
                    drawVerticalLine: false,
                    horizontalInterval: priceRange / 4,
                    getDrawingHorizontalLine: (value) => const FlLine(
                        color: AppColors.divider, strokeWidth: 0.5),
                  ),
                  titlesData: FlTitlesData(
                    leftTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 44,
                        getTitlesWidget: (value, meta) {
                          return Text('¥${value.toInt()}',
                              style: const TextStyle(
                                  fontSize: 10,
                                  color: AppColors.textSecondary));
                        },
                      ),
                    ),
                    bottomTitles: AxisTitles(
                      sideTitles: SideTitles(
                        showTitles: true,
                        reservedSize: 44,
                        interval: isSinglePoint ? 1 : 5,
                        getTitlesWidget: (value, meta) {
                          final index = value.toInt();
                          if (index < 0 || index >= aggregated.length) {
                            return const SizedBox.shrink();
                          }
                          return Transform.rotate(
                            angle: -0.785,
                            child: Padding(
                              padding: const EdgeInsets.only(top: 6),
                              child: Text(
                                DateFormat('M/d')
                                    .format(aggregated[index].date),
                                style: const TextStyle(
                                    fontSize: 9,
                                    color: AppColors.textSecondary),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    topTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                    rightTitles: const AxisTitles(
                        sideTitles: SideTitles(showTitles: false)),
                  ),
                  borderData: FlBorderData(show: false),
                  lineBarsData: [
                    LineChartBarData(
                      spots: spots,
                      isCurved: true,
                      curveSmoothness: 0.3,
                      color: AppColors.primary,
                      barWidth: 2,
                      dotData: FlDotData(show: isSinglePoint),
                      belowBarData: BarAreaData(
                          show: !isSinglePoint,
                          color: AppColors.primary.withValues(alpha: 0.1)),
                    ),
                  ],
                  lineTouchData: LineTouchData(
                    touchTooltipData: LineTouchTooltipData(
                      getTooltipItems: (touchedSpots) {
                        return touchedSpots.map((spot) {
                          final date = aggregated[spot.spotIndex].date;
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

  Widget _buildEmptyChart() {
    return const Padding(
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: AppSurface(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('30 天价格走势',
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary)),
            SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.show_chart,
                        size: 48, color: AppColors.textSecondary),
                    SizedBox(height: 8),
                    Text('暂无价格数据',
                        style: TextStyle(color: AppColors.textSecondary)),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
