import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/history_record.dart';
import '../../shared/services/api_client.dart';

class HistoryState {
  final List<HistoryRecord> records;
  final bool isLoading;
  final bool hasAttempted;
  final int? deletingId;
  final String? errorMsg;

  const HistoryState({
    this.records = const [],
    this.isLoading = false,
    this.hasAttempted = false,
    this.deletingId,
    this.errorMsg,
  });

  HistoryState copyWith({
    List<HistoryRecord>? records,
    bool? isLoading,
    bool? hasAttempted,
    int? deletingId,
    String? errorMsg,
  }) {
    return HistoryState(
      records: records ?? this.records,
      isLoading: isLoading ?? this.isLoading,
      hasAttempted: hasAttempted ?? this.hasAttempted,
      deletingId: deletingId,
      errorMsg: errorMsg,
    );
  }
}

class HistoryNotifier extends StateNotifier<HistoryState> {
  final ApiClient _api;

  HistoryNotifier(this._api) : super(const HistoryState());

  Future<void> loadRecords() async {
    state = state.copyWith(isLoading: true, hasAttempted: true, errorMsg: null);
    try {
      final data = await _api.getRecordList();
      final records = data
          .map((e) => HistoryRecord.fromJson(e as Map<String, dynamic>))
          .toList();
      state = state.copyWith(records: records, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: '加载历史记录失败');
    }
  }

  Future<void> deleteRecord(int id) async {
    state = state.copyWith(deletingId: id);
    try {
      await _api.deleteRecord(id);
      final updated = state.records.where((r) => r.id != id).toList();
      state = state.copyWith(records: updated, deletingId: null);
    } on ApiException catch (e) {
      state = state.copyWith(deletingId: null, errorMsg: e.message);
    } catch (e) {
      state = state.copyWith(deletingId: null, errorMsg: '删除失败');
    }
  }
}

final historyProvider =
    StateNotifierProvider<HistoryNotifier, HistoryState>((ref) {
  final api = ref.watch(apiClientProvider);
  return HistoryNotifier(api);
});
