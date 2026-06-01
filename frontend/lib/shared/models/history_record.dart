class HistoryRecord {
  final int id;
  final String searchSource;
  final int compareType;
  final DateTime createTime;

  const HistoryRecord({
    required this.id,
    required this.searchSource,
    required this.compareType,
    required this.createTime,
  });

  String get typeLabel {
    switch (compareType) {
      case 1:
        return '图片比价';
      case 2:
        return '链接比价';
      case 3:
        return '关键词比价';
      default:
        return '比价';
    }
  }

  String get typeIcon {
    switch (compareType) {
      case 1:
        return '📷';
      case 2:
        return '🔗';
      case 3:
        return '🔍';
      default:
        return '📋';
    }
  }

  String get displaySource {
    if (searchSource.length > 50) {
      return '${searchSource.substring(0, 50)}...';
    }
    return searchSource;
  }

  factory HistoryRecord.fromJson(Map<String, dynamic> json) {
    return HistoryRecord(
      id: json['id'] as int,
      searchSource: json['search_source'] as String? ?? '',
      compareType: json['compare_type'] as int? ?? 0,
      createTime: DateTime.parse(json['create_time'] as String),
    );
  }
}
