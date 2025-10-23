import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'constants/colors.dart';
import 'providers/auth_provider.dart';
import 'screens/auth_screens.dart';
import 'screens/debug_screen.dart';

// Placeholder screens for now
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('JobWise'),
        backgroundColor: AppColors.primary,
        actions: [
          IconButton(
            icon: const Icon(Icons.bug_report),
            tooltip: 'Debug Tools',
            onPressed: () {
              context.go('/debug');
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Logout',
            onPressed: () async {
              try {
                await ref.read(authProvider.notifier).logout();
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Logged out successfully')),
                  );
                }
              } catch (e) {
                if (context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Logout completed (local session cleared)')),
                  );
                }
              }
            },
          ),
        ],
      ),
      body: const Center(
        child: Text('Welcome to JobWise!'),
      ),
    );
  }
}

class App extends ConsumerStatefulWidget {
  const App({super.key});

  @override
  ConsumerState<App> createState() => _AppState();
}

class _AppState extends ConsumerState<App> {
  late final GoRouter _router;

  @override
  void initState() {
    super.initState();
    _router = GoRouter(
      initialLocation: '/login',
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/register',
          builder: (context, state) => const RegisterScreen(),
        ),
        GoRoute(
          path: '/home',
          builder: (context, state) => const HomeScreen(),
        ),
        GoRoute(
          path: '/debug',
          builder: (context, state) => const DebugScreen(),
        ),
      ],
      redirect: (context, state) {
        final authState = ref.read(authProvider);

        final isLoggedIn = authState.isAuthenticated;
        final isLoggingIn = state.matchedLocation == '/login';
        final isRegistering = state.matchedLocation == '/register';

        // If user is not logged in and not on login/register page, redirect to login
        if (!isLoggedIn && !isLoggingIn && !isRegistering) {
          return '/login';
        }

        // If user is logged in and on login/register page, redirect to home
        if (isLoggedIn && (isLoggingIn || isRegistering)) {
          return '/home';
        }

        // No redirect needed
        return null;
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    // Listen to auth state changes for navigation
    ref.listen<AuthState>(authProvider, (previous, next) {
      if (next.isAuthenticated && previous?.isAuthenticated != true) {
        // User just logged in, navigate to home
        _router.go('/home');
      } else if (!next.isAuthenticated && previous?.isAuthenticated == true) {
        // User just logged out, navigate to login
        _router.go('/login');
      }
    });

    return MaterialApp.router(
      title: 'JobWise',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          brightness: Brightness.light,
        ),
        useMaterial3: true,
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          filled: true,
          fillColor: AppColors.surface,
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            backgroundColor: AppColors.primary,
            foregroundColor: Colors.white,
          ),
        ),
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: AppColors.primary,
          ),
        ),
      ),
      routerConfig: _router,
    );
  }
}