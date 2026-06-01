import 'dart:math';
import '../models/compare_result.dart';
import '../models/goods.dart';

CompareResult mockCompareResult(String keyword) {
  final goodsName =
      keyword.isNotEmpty ? keyword : 'iPhone 16 Pro Max 256GB 原色钛金属';

  final compareList = [
    Goods(
      id: 2001,
      goodsName: goodsName,
      brand: 'Apple',
      model: 'iPhone 16 Pro Max',
      specParam: '256GB 原色钛金属',
      platform: '拼多多',
      shopName: '百亿补贴官方',
      originalPrice: 9999,
      realPrice: 8299,
      couponDesc: '百亿补贴 -1700',
      goodsUrl: 'https://pdd.com/example1',
      salesNum: 120000,
      score: 4.6,
      matchScore: 92,
      trustScore: 83,
    ),
    Goods(
      id: 2002,
      goodsName: goodsName,
      brand: 'Apple',
      model: 'iPhone 16 Pro Max',
      specParam: '256GB 原色钛金属',
      platform: '京东',
      shopName: 'Apple 产品京东自营旗舰店',
      originalPrice: 9999,
      realPrice: 8799,
      couponDesc: '满 9000 减 200',
      goodsUrl: 'https://jd.com/example1',
      salesNum: 85000,
      score: 4.9,
      matchScore: 96,
      trustScore: 94,
    ),
    Goods(
      id: 2003,
      goodsName: goodsName,
      brand: 'Apple',
      model: 'iPhone 16 Pro Max',
      specParam: '256GB 沙漠色钛金属',
      platform: '淘宝',
      shopName: '天猫 Apple Store 官方旗舰店',
      originalPrice: 9999,
      realPrice: 8999,
      couponDesc: '88VIP 专享',
      goodsUrl: 'https://taobao.com/example1',
      salesNum: 42000,
      score: 4.8,
      matchScore: 89,
      trustScore: 91,
    ),
  ];

  final realPrices =
      compareList.where((g) => g.isOnSale).map((g) => g.realPrice).toList();
  final minPrice = realPrices.reduce((a, b) => a < b ? a : b);
  final maxPrice = realPrices.reduce((a, b) => a > b ? a : b);
  final avgPrice = realPrices.reduce((a, b) => a + b) / realPrices.length;
  final priceHistory = _generate30DayPrices(avgPrice, amplitude: 600);

  return CompareResult(
    goodsInfo: goodsName,
    aiAnalysis: AiAnalysis(
      priceLevel: _judgePriceLevel(minPrice, avgPrice),
      buyAdvice:
          '当前最低到手价 ¥${minPrice.toInt()}，低于均价 ¥${avgPrice.toInt()}，建议优先选择高可信店铺。',
      pricePrediction: '近 7 天价格大概率平稳，小幅波动时可以开启降价提醒再入手。',
    ),
    priceHistory: priceHistory,
    compareList: compareList,
    extractedInfo: ExtractedInfo(
      goodsName: 'iPhone 16 Pro Max',
      brand: 'Apple',
      model: 'iPhone 16 Pro Max',
      price: '¥${minPrice.toInt()}-¥${maxPrice.toInt()}',
      category: '手机',
      specs: '256GB 原色钛金属 A18 Pro 芯片',
    ),
    isMockData: true,
  );
}

String _judgePriceLevel(double current, double avg) {
  final ratio = (current - avg) / avg;
  if (ratio < -0.05) return '偏低';
  if (ratio > 0.05) return '偏高';
  return '适中';
}

List<PricePoint> _generate30DayPrices(double centerPrice,
    {double amplitude = 500}) {
  final now = DateTime.now();
  final rng = Random(42);
  return List.generate(30, (i) {
    final date = now.subtract(Duration(days: 29 - i));
    final wave = sin(i / 30.0 * 2 * pi) * amplitude * 0.4;
    final trend = -amplitude * 0.15 * (i / 29.0);
    final noise = (rng.nextDouble() - 0.5) * amplitude * 0.2;
    final price = centerPrice + wave + trend + noise;
    return PricePoint(
        date: date, price: double.parse(price.toStringAsFixed(0)));
  });
}
