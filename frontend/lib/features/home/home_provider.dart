import 'package:flutter_riverpod/flutter_riverpod.dart';

class HomeState {
  final String searchKeyword;
  final bool isSearching;

  const HomeState({this.searchKeyword = '', this.isSearching = false});

  HomeState copyWith({String? searchKeyword, bool? isSearching}) {
    return HomeState(
      searchKeyword: searchKeyword ?? this.searchKeyword,
      isSearching: isSearching ?? this.isSearching,
    );
  }
}

class HomeNotifier extends StateNotifier<HomeState> {
  HomeNotifier() : super(const HomeState());

  void updateKeyword(String keyword) {
    state = state.copyWith(searchKeyword: keyword);
  }
}

final homeProvider = StateNotifierProvider<HomeNotifier, HomeState>((ref) {
  return HomeNotifier();
});
