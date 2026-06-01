import 'dart:typed_data';
import 'dart:async';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart'
    show TargetPlatform, defaultTargetPlatform, kIsWeb;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

String get _baseUrl {
  const configuredUrl = String.fromEnvironment('API_BASE_URL');
  if (configuredUrl.isNotEmpty) {
    return configuredUrl;
  }
  if (kIsWeb) {
    return 'http://127.0.0.1:8000';
  }
  if (defaultTargetPlatform == TargetPlatform.android) {
    return 'http://127.0.0.1:8000';
  }
  return 'http://127.0.0.1:8000';
}

const _tokenKey = 'auth_token';
const useMockOnApiFailure =
    bool.fromEnvironment('USE_MOCK_ON_API_FAILURE', defaultValue: false);

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());

class ApiClient {
  late final Dio _dio;
  String? _token;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 120),
    ));
    _dio.interceptors.add(_authInterceptor());
  }

  Interceptor _authInterceptor() {
    return InterceptorsWrapper(
      onRequest: (options, handler) async {
        if (_token == null) {
          final prefs = await SharedPreferences.getInstance();
          _token = prefs.getString(_tokenKey);
        }
        if (_token != null && _token!.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $_token';
        }
        handler.next(options);
      },
    );
  }

  Future<void> saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
  }

  Future<void> clearToken() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
  }

  Future<bool> get hasToken async {
    if (_token != null && _token!.isNotEmpty) return true;
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(_tokenKey);
    return _token != null && _token!.isNotEmpty;
  }

  Future<Map<String, dynamic>> register({
    required String username,
    required String password,
    String? phone,
  }) async {
    final body = <String, dynamic>{'username': username, 'password': password};
    if (phone != null && phone.isNotEmpty) body['phone'] = phone;
    return await _post('/api/user/register', body, auth: false);
  }

  Future<Map<String, dynamic>> login({
    required String phone,
    required String password,
  }) async {
    return await _post(
        '/api/user/login', {'phone': phone, 'password': password},
        auth: false);
  }

  Future<Map<String, dynamic>> getUserInfo() async {
    return await _get('/api/user/info');
  }

  Future<void> updateUser({String? username, String? avatar}) async {
    final body = <String, dynamic>{};
    if (username != null) body['username'] = username;
    if (avatar != null) body['avatar'] = avatar;
    await _put('/api/user/update', body);
  }

  Future<Map<String, dynamic>> compareByImage(Uint8List imageBytes) async {
    final file = MultipartFile.fromBytes(imageBytes, filename: 'image.jpg');
    final formData = FormData.fromMap({'file': file});
    return await _multipart('/api/compare/image', formData, auth: false);
  }

  Future<Map<String, dynamic>> compareByUrl(String goodsUrl) async {
    return await _post('/api/compare/url', {'goods_url': goodsUrl},
        auth: false);
  }

  Future<Map<String, dynamic>> compareByKeyword(String keyword) async {
    return await _get('/api/compare/search',
        query: {'keyword': keyword}, auth: false);
  }

  Future<Map<String, dynamic>> agentChat({
    required String message,
    List<Map<String, String>> history = const [],
  }) async {
    return await _post(
      '/api/agent/chat',
      {'message': message, 'history': history},
      auth: true,
    );
  }

  Future<Map<String, dynamic>> agentChatImage({
    required Uint8List imageBytes,
    String message = '',
  }) async {
    final file =
        MultipartFile.fromBytes(imageBytes, filename: 'agent-image.jpg');
    final formData = FormData.fromMap({'file': file, 'message': message});
    return await _multipart('/api/agent/chat/image', formData, auth: true);
  }

  Future<List<dynamic>> getRecordList() async {
    return await _get('/api/record/list');
  }

  Future<void> deleteRecord(int recordId) async {
    await _delete('/api/record/delete',
        query: {'record_id': recordId.toString()});
  }

  Future<Map<String, dynamic>> getGoodsPriceHistory(int goodsId) async {
    return await _get('/api/goods/price/history',
        query: {'goods_id': goodsId.toString()});
  }

  Future<dynamic> _get(String path,
      {Map<String, String>? query, bool auth = true}) async {
    return _request('GET', path, query: query, auth: auth);
  }

  Future<dynamic> _post(String path, Map<String, dynamic> body,
      {bool auth = true}) async {
    return _request('POST', path, body: body, auth: auth);
  }

  Future<dynamic> _put(String path, Map<String, dynamic> body,
      {bool auth = true}) async {
    return _request('PUT', path, body: body, auth: auth);
  }

  Future<dynamic> _delete(String path,
      {Map<String, String>? query, bool auth = true}) async {
    return _request('DELETE', path, query: query, auth: auth);
  }

  Future<dynamic> _multipart(String path, FormData formData,
      {bool auth = true}) async {
    try {
      final response = await _dio.post(path,
          data: formData,
          options: Options(method: 'POST', extra: {'auth': auth}));
      return _unwrapResponse(response);
    } on ApiException {
      rethrow;
    } on DioException catch (e) {
      throw _mapDioException(e);
    } catch (e) {
      throw ApiException(-1, '图片上传失败: $e');
    }
  }

  Future<dynamic> _request(
    String method,
    String path, {
    Map<String, String>? query,
    Map<String, dynamic>? body,
    bool auth = true,
  }) async {
    try {
      final response = await _dio.request(
        path,
        data: body,
        queryParameters: query,
        options: Options(
            method: method,
            contentType: 'application/json',
            extra: {'auth': auth}),
      );
      return _unwrapResponse(response);
    } on ApiException {
      rethrow;
    } on DioException catch (e) {
      throw _mapDioException(e);
    }
  }

  dynamic _unwrapResponse(Response<dynamic> response) {
    final json = response.data as Map<String, dynamic>;
    final code = json['code'] as int;

    if (code == 401) {
      unawaited(clearToken());
      throw ApiException(401, json['msg'] as String? ?? '请先登录');
    }
    if (code != 200) {
      throw ApiException(code, json['msg'] as String? ?? '请求失败');
    }
    return json['data'];
  }

  ApiException _mapDioException(DioException e) {
    if (e.type == DioExceptionType.badResponse) {
      final data = e.response?.data;
      if (data is Map<String, dynamic>) {
        final code = data['code'];
        final msg = data['msg'];
        if (msg is String && msg.isNotEmpty) {
          return ApiException(code is int ? code : -1, msg);
        }
      }
      return ApiException(
        e.response?.statusCode ?? -1,
        '请求失败，请检查输入内容后重试',
      );
    }
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout ||
        e.type == DioExceptionType.connectionError) {
      return ApiException(-1, '网络连接失败，请检查后端服务或网络设置');
    }
    return ApiException(-1, '网络请求失败: ${e.message}');
  }
}

class ApiException implements Exception {
  final int code;
  final String message;

  ApiException(this.code, this.message);

  @override
  String toString() => message;
}
