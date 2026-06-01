import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'features/auth/login_page.dart';
import 'features/auth/auth_provider.dart';
import 'features/agent/agent_page.dart';
import 'features/home/home_page.dart';
import 'features/camera/camera_page.dart';
import 'features/compare/compare_page.dart';
import 'features/history/history_page.dart';
import 'features/profile/profile_page.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/login',
    redirect: (context, state) {
      final isLoggedIn = ref.read(authProvider).isLoggedIn;
      final isLoginRoute = state.matchedLocation == '/login';
      if (!isLoggedIn && !isLoginRoute) return '/login';
      if (isLoggedIn && isLoginRoute) return '/home';
      return null;
    },
    routes: [
      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginPage(),
      ),
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) {
          final location = state.matchedLocation;
          int currentIndex = 0;
          if (location.startsWith('/history')) {
            currentIndex = 1;
          } else if (location.startsWith('/agent')) {
            currentIndex = 2;
          } else if (location.startsWith('/profile')) {
            currentIndex = 3;
          }

          return Scaffold(
            body: child,
            bottomNavigationBar: SafeArea(
              top: false,
              child: Container(
                margin: const EdgeInsets.fromLTRB(14, 0, 14, 10),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.06),
                      blurRadius: 20,
                      offset: const Offset(0, 8),
                    ),
                  ],
                ),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(18),
                  child: BottomNavigationBar(
                    currentIndex: currentIndex,
                    onTap: (index) {
                      switch (index) {
                        case 0:
                          context.go('/home');
                          break;
                        case 1:
                          context.go('/history');
                          break;
                        case 2:
                          context.go('/agent');
                          break;
                        case 3:
                          context.go('/profile');
                          break;
                      }
                    },
                    items: const [
                      BottomNavigationBarItem(
                          icon: Icon(Icons.home_outlined),
                          activeIcon: Icon(Icons.home),
                          label: '首页'),
                      BottomNavigationBarItem(
                          icon: Icon(Icons.history_outlined),
                          activeIcon: Icon(Icons.history),
                          label: '历史'),
                      BottomNavigationBarItem(
                          icon: Icon(Icons.support_agent_outlined),
                          activeIcon: Icon(Icons.support_agent),
                          label: 'AI客服'),
                      BottomNavigationBarItem(
                          icon: Icon(Icons.person_outline),
                          activeIcon: Icon(Icons.person),
                          label: '我的'),
                    ],
                  ),
                ),
              ),
            ),
          );
        },
        routes: [
          GoRoute(
            path: '/home',
            name: 'home',
            builder: (context, state) => const HomePage(),
          ),
          GoRoute(
            path: '/history',
            name: 'history',
            builder: (context, state) => const HistoryPage(),
          ),
          GoRoute(
            path: '/agent',
            name: 'agent',
            builder: (context, state) => const AgentPage(),
          ),
          GoRoute(
            path: '/profile',
            name: 'profile',
            builder: (context, state) => const ProfilePage(),
          ),
        ],
      ),
      GoRoute(
        path: '/camera',
        name: 'camera',
        builder: (context, state) => const CameraPage(),
      ),
      GoRoute(
        path: '/compare-result',
        name: 'compare-result',
        builder: (context, state) => const ComparePage(),
      ),
    ],
  );
});
