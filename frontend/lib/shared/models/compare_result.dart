import 'goods.dart';

class ExtractedInfo {
  final String goodsName;
  final String brand;
  final String model;
  final String price;
  final String category;
  final String specs;

  const ExtractedInfo({
    this.goodsName = '',
    this.brand = '',
    this.model = '',
    this.price = '',
    this.category = '',
    this.specs = '',
  });

  factory ExtractedInfo.fromJson(Map<String, dynamic> json) {
    return ExtractedInfo(
      goodsName: json['goods_name'] as String? ?? '',
      brand: json['brand'] as String? ?? '',
      model: json['model'] as String? ?? '',
      price: json['price'] as String? ?? '',
      category: json['category'] as String? ?? '',
      specs: json['specs'] as String? ?? '',
    );
  }
}

class PricePoint {
  final DateTime date;
  final double price;
  final int goodsId;

  const PricePoint({required this.date, required this.price, this.goodsId = 0});

  factory PricePoint.fromJson(Map<String, dynamic> json) {
    return PricePoint(
      date: DateTime.parse(json['date'] as String),
      price: (json['price'] as num).toDouble(),
      goodsId: json['goods_id'] as int? ?? 0,
    );
  }
}

class AiAnalysis {
  final String priceLevel;
  final String buyAdvice;
  final String pricePrediction;

  const AiAnalysis({
    required this.priceLevel,
    required this.buyAdvice,
    required this.pricePrediction,
  });

  factory AiAnalysis.fromJson(Map<String, dynamic> json) {
    return AiAnalysis(
      priceLevel: json['price_level'] as String? ?? '',
      buyAdvice: json['buy_advice'] as String? ?? '',
      pricePrediction: json['price_prediction'] as String? ?? '',
    );
  }
}

class CompareResult {
  final String goodsInfo;
  final AiAnalysis aiAnalysis;
  final List<PricePoint> priceHistory;
  final List<Goods> compareList;
  final ExtractedInfo? extractedInfo;
  final String? ossUrl;
  final bool isMockData;

  const CompareResult({
    required this.goodsInfo,
    required this.aiAnalysis,
    required this.priceHistory,
    required this.compareList,
    this.extractedInfo,
    this.ossUrl,
    this.isMockData = false,
  });

  factory CompareResult.fromJson(Map<String, dynamic> json) {
    return CompareResult(
      goodsInfo: json['goods_info'] as String? ?? '',
      aiAnalysis: AiAnalysis.fromJson(json['ai_analysis'] as Map<String, dynamic>? ?? {}),
      priceHistory: (json['price_history'] as List<dynamic>?)
              ?.map((e) => PricePoint.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      compareList: (json['compare_list'] as List<dynamic>?)
              ?.map((e) => Goods.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      extractedInfo: json['extracted_info'] != null
          ? ExtractedInfo.fromJson(json['extracted_info'] as Map<String, dynamic>)
          : null,
      ossUrl: json['oss_url'] as String?,
      isMockData: false,
    );
  }
}
