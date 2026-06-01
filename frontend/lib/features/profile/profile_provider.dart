import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../shared/models/user.dart';
import '../../shared/services/api_client.dart';

class ProfileState {
  final User? user;
  final bool isLoading;
  final bool hasAttempted;
  final bool isSaving;
  final String? errorMsg;

  const ProfileState(
      {this.user,
      this.isLoading = false,
      this.hasAttempted = false,
      this.isSaving = false,
      this.errorMsg});

  ProfileState copyWith(
      {User? user,
      bool? isLoading,
      bool? hasAttempted,
      bool? isSaving,
      String? errorMsg}) {
    return ProfileState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      hasAttempted: hasAttempted ?? this.hasAttempted,
      isSaving: isSaving ?? this.isSaving,
      errorMsg: errorMsg,
    );
  }
}

class ProfileNotifier extends StateNotifier<ProfileState> {
  final ApiClient _api;

  ProfileNotifier(this._api) : super(const ProfileState());

  Future<void> loadUser() async {
    state = state.copyWith(isLoading: true, hasAttempted: true, errorMsg: null);
    try {
      final data = await _api.getUserInfo();
      final user = User.fromJson(data);
      state = state.copyWith(user: user, isLoading: false);
    } on ApiException catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: e.message);
    } catch (e) {
      state = state.copyWith(isLoading: false, errorMsg: '获取用户信息失败');
    }
  }

  Future<bool> updateProfile({String? username, String? avatar}) async {
    state = state.copyWith(isSaving: true, errorMsg: null);
    try {
      await _api.updateUser(username: username, avatar: avatar);
      if (state.user != null) {
        final updated = User(
          id: state.user!.id,
          username: username ?? state.user!.username,
          phone: state.user!.phone,
          avatar: avatar ?? state.user!.avatar,
        );
        state = state.copyWith(user: updated, isSaving: false);
      } else {
        state = state.copyWith(isSaving: false);
      }
      return true;
    } on ApiException catch (e) {
      state = state.copyWith(isSaving: false, errorMsg: e.message);
      return false;
    } catch (e) {
      state = state.copyWith(isSaving: false, errorMsg: '保存失败');
      return false;
    }
  }
}

final profileProvider =
    StateNotifierProvider<ProfileNotifier, ProfileState>((ref) {
  final api = ref.watch(apiClientProvider);
  return ProfileNotifier(api);
});
