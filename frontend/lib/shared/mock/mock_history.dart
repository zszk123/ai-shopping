import '../models/history_record.dart';

/// 生成模拟比价历史记录（当后端不可用时用于 UI 展示）
List<HistoryRecord> mockHistoryRecords(int userId) {
  final now = DateTime.now();
  return [
    HistoryRecord(
      id: 1,
      searchSource: '索尼 WH-1000XM5 头戴式降噪耳机 黑色',
      compareType: 1,
      createTime: now.subtract(const Duration(hours: 2)),
    ),
    HistoryRecord(
      id: 2,
      searchSource: 'https://item.jd.com/1000123456.html',
      compareType: 2,
      createTime: now.subtract(const Duration(days: 1)),
    ),
    HistoryRecord(
      id: 3,
      searchSource: '蓝牙耳机 降噪',
      compareType: 3,
      createTime: now.subtract(const Duration(days: 2)),
    ),
    HistoryRecord(
      id: 4,
      searchSource: 'iPhone 15 Pro Max 256GB 原色钛金属',
      compareType: 1,
      createTime: now.subtract(const Duration(days: 5)),
    ),
    HistoryRecord(
      id: 5,
      searchSource: '机械键盘 青轴 无线',
      compareType: 3,
      createTime: now.subtract(const Duration(days: 7)),
    ),
  ];
}
