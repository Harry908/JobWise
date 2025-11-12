import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'constants/colors.dart';
import 'providers/auth_provider.dart';
import 'providers/profile_provider.dart';
import 'screens/auth_screens.dart';
import 'screens/debug_screen.dart';
import 'screens/job_browse_screen.dart';
import 'screens/job_detail_screen.dart';
import 'screens/job_list_screen.dart';
import 'screens/job_paste_screen.dart';
import 'screens/profile_edit_screen.dart';
import 'screens/profile_view_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/generation_options_screen.dart';
import 'screens/generation_progress_screen.dart';
import 'screens/generation_result_screen.dart';
import 'screens/generation_history_screen.dart';
import 'models/job.dart';
import 'models/generation.dart';

// Placeholder screens for now
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final profileState = ref.watch(profileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('JobWise'),
        backgroundColor: AppColors.primary,
        actions: [
          IconButton(
            icon: const Icon(Icons.person),
            tooltip: 'My Profile',
            onPressed: () {
              if (profileState.profile != null) {
                context.push('/profile/view');
              } else {
                context.push('/profile/edit');
              }
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            tooltip: 'Settings',
            onPressed: () {
              context.push('/settings');
            },
          ),
          IconButton(
            icon: const Icon(Icons.bug_report),
            tooltip: 'Debug Tools',
            onPressed: () {
              context.push('/debug');
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
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Icon(
              Icons.work,
              size: 80,
              color: AppColors.primary,
            ),
            const SizedBox(height: 24),
            Text(
              'Welcome to JobWise!',
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                color: AppColors.primary,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            Text(
              'Your AI-powered job application assistant',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            if (profileState.profile != null) ...[
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    context.push('/jobs');
                  },
                  icon: const Icon(Icons.work),
                  label: const Text('My Jobs'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () {
                    context.push('/jobs/browse');
                  },
                  icon: const Icon(Icons.search),
                  label: const Text('Browse Jobs'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    context.push('/generations');
                  },
                  icon: const Icon(Icons.auto_awesome),
                  label: const Text('Generation History'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    context.push('/profile/view');
                  },
                  icon: const Icon(Icons.person),
                  label: const Text('View Profile'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () {
                    context.push('/profile/edit');
                  },
                  icon: const Icon(Icons.edit),
                  label: const Text('Edit Profile'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
            ] else ...[
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () {
                    context.push('/profile/edit');
                  },
                  icon: const Icon(Icons.person_add),
                  label: const Text('Create Profile'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    textStyle: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
            ],
            const SizedBox(height: 16),
            if (authState.user != null)
              Text(
                'Logged in as: ${authState.user!.email}',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),
          ],
        ),
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
        GoRoute(
          path: '/settings',
          builder: (context, state) => const SettingsScreen(),
        ),
        GoRoute(
          path: '/profile/edit',
          builder: (context, state) => const ProfileEditScreen(),
        ),
        GoRoute(
          path: '/profile/view',
          builder: (context, state) => const ProfileViewScreen(),
        ),
        // Job routes
        GoRoute(
          path: '/jobs',
          builder: (context, state) => const JobListScreen(),
        ),
        GoRoute(
          path: '/jobs/paste',
          builder: (context, state) => const JobPasteScreen(),
        ),
        GoRoute(
          path: '/jobs/browse',
          builder: (context, state) => const JobBrowseScreen(),
        ),
        GoRoute(
          path: '/jobs/:id',
          builder: (context, state) {
            final jobId = state.pathParameters['id']!;
            return JobDetailScreen(jobId: jobId);
          },
        ),
        // Generation routes
        GoRoute(
          path: '/generations',
          builder: (context, state) => const GenerationHistoryScreen(),
        ),
        GoRoute(
          path: '/generations/options',
          builder: (context, state) {
            final job = state.extra as Job;
            final documentTypeStr = state.uri.queryParameters['type'];
            final documentType = documentTypeStr == 'cover_letter'
                ? DocumentType.coverLetter
                : DocumentType.resume;
            return GenerationOptionsScreen(
              job: job,
              documentType: documentType,
            );
          },
        ),
        GoRoute(
          path: '/generations/:id/progress',
          builder: (context, state) {
            final generationId = state.pathParameters['id']!;
            return GenerationProgressScreen(generationId: generationId);
          },
        ),
        GoRoute(
          path: '/generations/:id/result',
          builder: (context, state) {
            final generationId = state.pathParameters['id']!;
            return GenerationResultScreen(generationId: generationId);
          },
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