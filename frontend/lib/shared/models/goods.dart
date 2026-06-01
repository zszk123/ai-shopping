class Goods {
  final int id;
  final String goodsName;
  final String brand;
  final String model;
  final String specParam;
  final String platform;
  final String shopName;
  final double originalPrice;
  final double realPrice;
  final String couponDesc;
  final String goodsImg;
  final String goodsUrl;
  final int salesNum;
  final double score;
  final int saleStatus;
  final double matchScore;
  final double trustScore;

  const Goods({
    required this.id,
    required this.goodsName,
    this.brand = '',
    this.model = '',
    this.specParam = '',
    required this.platform,
    this.shopName = '',
    this.originalPrice = 0,
    required this.realPrice,
    this.couponDesc = '',
    this.goodsImg = '',
    required this.goodsUrl,
    this.salesNum = 0,
    this.score = 0,
    this.saleStatus = 1,
    this.matchScore = 0,
    this.trustScore = 0,
  });

  bool get isOnSale => saleStatus == 1;
  bool get isOffShelf => saleStatus == 0;

  String get platformLabel {
    switch (platform) {
      case 'jingdong':
      case '京东':
        return '京东';
      case 'taobao':
      case '淘宝':
        return '淘宝';
      case 'pdd':
      case '拼多多':
        return '拼多多';
      case 'douyin':
      case '抖音':
        return '抖音';
      default:
        return platform;
    }
  }

  String get salesText {
    if (salesNum >= 10000) return '${(salesNum / 10000).toStringAsFixed(1)}万+';
    if (salesNum >= 1000) return '${(salesNum / 1000).toStringAsFixed(1)}k+';
    return '$salesNum';
  }

  String get trustLabel {
    if (trustScore >= 80) return '高可信';
    if (trustScore >= 60) return '中可信';
    return '需核验';
  }

  factory Goods.fromJson(Map<String, dynamic> json) {
    return Goods(
      id: json['goods_id'] as int? ?? 0,
      goodsName: json['goods_name'] as String? ?? '',
      brand: json['brand'] as String? ?? '',
      model: json['model'] as String? ?? '',
      specParam: json['spec_param'] as String? ?? '',
      platform: json['platform'] as String? ?? '',
      shopName: json['shop_name'] as String? ?? '',
      originalPrice: (json['original_price'] as num?)?.toDouble() ?? 0,
      realPrice: (json['real_price'] as num?)?.toDouble() ?? 0,
      couponDesc: json['coupon_desc'] as String? ?? '',
      goodsImg: json['goods_img'] as String? ?? '',
      goodsUrl: json['goods_url'] as String? ?? '',
      salesNum: json['sales_num'] as int? ?? 0,
      score: (json['score'] as num?)?.toDouble() ?? 0,
      saleStatus: json['sale_status'] as int? ?? 1,
      matchScore: (json['match_score'] as num?)?.toDouble() ?? 0,
      trustScore: (json['trust_score'] as num?)?.toDouble() ?? 0,
    );
  }
}
