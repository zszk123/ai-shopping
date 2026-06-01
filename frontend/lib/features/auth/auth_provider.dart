import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/user.dart';
import '../../shared/services/api_client.dart';

enum AuthMode { login, register }

class AuthState {
  final AuthMode mode;
  final bool isLoading;
  final String? errorMsg;
  final User? currentUser;
  final String? token;
  final bool isLoggedIn;

  const AuthState({
    this.mode = AuthMode.login,
    this.isLoading = false,
    this.errorMsg,
    this.currentUser,
    this.token,
    this.isLoggedIn = false,
  });

  AuthState copyWith({
    AuthMode? mode,
    bool? isLoading,
    String? errorMsg,
    User? currentUser,
    String? token,
    bool? isLoggedIn,
  }) {
    return AuthState(
      mode: mode ?? this.mode,
      isLoading: isLoading ?? this.isLoading,
      errorMsg: errorMsg,
      currentUser: currentUser ?? this.currentUser,
      token: token ?? this.token,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _api;

  AuthNotifier(this._api) : super(const AuthState());

  Future<void> tryAutoLogin() async {
    if (await _api.hasToken) {
      try {
        final data = await _api.getUserInfo();
        final user = User.fromJson(data);
        state = state.copyWith(isLoggedIn: true, currentUser: user);
      } catch (_) {
        await _api.clearToken();
      }
    }
  }

  void toggleMode() {
    state = state.copyWith(
      mode: state.mode == AuthMode.login ? AuthMode.register : AuthMode.login,
      errorMsg: null,
    );
  }

  Future<void> login(String phone, String password) async {
    if (phone.isEmpty || password.isEmpty) {
      state = state.copyWith(errorMsg: '请输入手机号和密码');
      return;
    }
    if (phone.length != 11) {
      state = state.copyWith(errorMsg: '请输入正确的11位手机号');
      return;
    }
    if (password.length < 6) {
      state = state.copyWith(errorMsg: '密码至少6位');
      return;
    }

    state = state.copyWith(isLoading: true, errorMsg: null);

    try {
      final data = await _api.login(phone: phone, password: password);
      final token = data['token'] as String;
      await _api.saveToken(token);

      state = state.copyWith(
        isLoading: false,
        isLoggedIn: true,
        token: token,
      );

      final info = await _api.getUserInfo();
      final user = User.fromJson(info);
      state = state.copyWith(currentUser: user);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: '登录失败，请稍后重试');
    }
  }

  Future<void> register(String phone, String password, String username) async {
    if (phone.isEmpty || password.isEmpty || username.isEmpty) {
      state = state.copyWith(errorMsg: '请填写所有字段');
      return;
    }
    if (phone.length != 11) {
      state = state.copyWith(errorMsg: '请输入正确的11位手机号');
      return;
    }
    if (password.length < 6) {
      state = state.copyWith(errorMsg: '密码至少6位');
      return;
    }

    state = state.copyWith(isLoading: true, errorMsg: null);

    try {
      final data = await _api.register(
        username: username,
        password: password,
        phone: phone,
      );
      final token = data['token'] as String;
      await _api.saveToken(token);

      final user = User(
        id: data['user_id'] as int? ?? 0,
        username: username,
        phone: phone,
      );

      state = state.copyWith(
        isLoading: false,
        isLoggedIn: true,
        currentUser: user,
        token: token,
      );
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: '注册失败，请稍后重试');
    }
  }

  Future<void> logout() async {
    await _api.clearToken();
    state = const AuthState();
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final api = ref.watch(apiClientProvider);
  return AuthNotifier(api);
});
