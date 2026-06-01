import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/compare_result.dart';
import '../../shared/services/api_client.dart';
import '../../shared/mock/mock_compare.dart';

class SearchContext {
  final int compareType; // 1=image, 2=url, 3=keyword
  final String searchSource;

  const SearchContext({required this.compareType, required this.searchSource});
}

final pendingSearchProvider = StateProvider<SearchContext?>((ref) => null);

enum CompareStatus { idle, loading, done, error }

const Object _unset = Object();

class CompareState {
  final CompareResult? result;
  final CompareStatus status;
  final String? errorMsg;
  final SearchContext? lastSearch;
  final Uint8List? lastImageBytes;

  const CompareState({
    this.result,
    this.status = CompareStatus.idle,
    this.errorMsg,
    this.lastSearch,
    this.lastImageBytes,
  });

  CompareState copyWith({
    Object? result = _unset,
    CompareStatus? status,
    Object? errorMsg = _unset,
    Object? lastSearch = _unset,
    Object? lastImageBytes = _unset,
  }) {
    return CompareState(
      result:
          identical(result, _unset) ? this.result : result as CompareResult?,
      status: status ?? this.status,
      errorMsg:
          identical(errorMsg, _unset) ? this.errorMsg : errorMsg as String?,
      lastSearch: identical(lastSearch, _unset)
          ? this.lastSearch
          : lastSearch as SearchContext?,
      lastImageBytes: identical(lastImageBytes, _unset)
          ? this.lastImageBytes
          : lastImageBytes as Uint8List?,
    );
  }
}

class CompareNotifier extends StateNotifier<CompareState> {
  final ApiClient _api;
  int _requestSerial = 0;

  CompareNotifier(this._api) : super(const CompareState());

  void loadFromContext(SearchContext ctx) {
    switch (ctx.compareType) {
      case 1:
        final imageBytes = state.lastImageBytes;
        if (imageBytes == null) {
          state = state.copyWith(
            result: null,
            status: CompareStatus.error,
            errorMsg: '没有可重试的图片，请重新选择图片。',
            lastSearch: ctx,
          );
          return;
        }
        compareByImage(imageBytes);
        break;
      case 2:
        compareByUrl(ctx.searchSource);
        break;
      case 3:
        compareByKeyword(ctx.searchSource);
        break;
      default:
        state = state.copyWith(
            status: CompareStatus.error, errorMsg: '未知的比价类型', lastSearch: ctx);
    }
  }

  Future<void> retry() async {
    final ctx = state.lastSearch;
    if (ctx != null) {
      loadFromContext(ctx);
    }
  }

  Future<void> compareByImage(Uint8List imageBytes) async {
    final requestId = _startRequest();
    const ctx = SearchContext(compareType: 1, searchSource: 'image');
    state = state.copyWith(
      result: null,
      status: CompareStatus.loading,
      errorMsg: null,
      lastSearch: ctx,
      lastImageBytes: imageBytes,
    );
    try {
      final data = await _api.compareByImage(imageBytes);
      if (!_isCurrentRequest(requestId)) return;
      state = state.copyWith(
        result: CompareResult.fromJson(data),
        status: CompareStatus.done,
        errorMsg: null,
      );
    } on ApiException catch (e) {
      if (!_isCurrentRequest(requestId)) return;
      _handleFailure(_friendlyError(e.message));
    } on FormatException catch (e) {
      if (!_isCurrentRequest(requestId)) return;
      _handleFailure('数据解析失败: ${e.message}');
    }
  }

  Future<void> compareByUrl(String url) async {
    final requestId = _startRequest();
    final ctx = SearchContext(compareType: 2, searchSource: url);
    state = state.copyWith(
      result: null,
      status: CompareStatus.loading,
      errorMsg: null,
      lastSearch: ctx,
      lastImageBytes: null,
    );
    try {
      final data = await _api.compareByUrl(url);
      if (!_isCurrentRequest(requestId)) return;
      state = state.copyWith(
        result: CompareResult.fromJson(data),
        status: CompareStatus.done,
        errorMsg: null,
      );
    } on ApiException catch (e) {
      if (!_isCurrentRequest(requestId)) return;
      _handleFailure(_friendlyError(e.message));
    } on FormatException catch (e) {
      if (!_isCurrentRequest(requestId)) return;
      _handleFailure('数据解析失败: ${e.message}');
    }
  }

  Future<void> compareByKeyword(String keyword) async {
    final requestId = _startRequest();
    final ctx = SearchContext(compareType: 3, searchSource: keyword);
    state = state.copyWith(
      result: null,
      status: CompareStatus.loading,
      errorMsg: null,
      lastSearch: ctx,
      lastImageBytes: null,
    );
    try {
      final data = await _api.compareByKeyword(keyword);
      if (!_isCurrentRequest(requestId)) return;
      state = state.copyWith(
        result: CompareResult.fromJson(data),
        status: CompareStatus.done,
        errorMsg: null,
      );
    } on ApiException catch (e) {
      if (!_isCurrentRequest(requestId)) return;
      _handleFailure(_friendlyError(e.message));
    } on FormatException catch (e) {
      if (!_isCurrentRequest(requestId)) return;
      _handleFailure('数据解析失败: ${e.message}');
    }
  }

  void _handleFailure(String reason) {
    if (useMockOnApiFailure) {
      state = state.copyWith(
        result: mockCompareResult(''),
        status: CompareStatus.done,
        errorMsg: reason,
      );
      return;
    }

    state = state.copyWith(
      result: null,
      status: CompareStatus.error,
      errorMsg: reason,
    );
  }

  void reset() {
    _requestSerial++;
    state = const CompareState();
  }

  int _startRequest() {
    _requestSerial++;
    return _requestSerial;
  }

  bool _isCurrentRequest(int requestId) {
    return requestId == _requestSerial;
  }

  String _friendlyError(String message) {
    if (message.contains('AccessDenied') ||
        message.contains('403') ||
        message.contains('DashScope 视觉模型无访问权限')) {
      return 'AI 识图服务暂时不可用：当前 DashScope 账号没有视觉模型访问权限。请检查 API Key 和模型开通状态。';
    }
    if (message.contains('OSS')) {
      return '图片上传服务暂时不可用，请检查 OSS 配置后重试。';
    }
    if (message.contains('connection') || message.contains('网络')) {
      return '网络连接失败，请确认后端服务已经启动。';
    }
    return message;
  }
}

final compareProvider =
    StateNotifierProvider<CompareNotifier, CompareState>((ref) {
  final api = ref.watch(apiClientProvider);
  return CompareNotifier(api);
});
