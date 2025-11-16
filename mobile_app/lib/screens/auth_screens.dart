import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants/colors.dart';
import '../constants/text_styles.dart';
import '../providers/auth_provider.dart';
import '../utils/validators.dart';
import '../widgets/loading_overlay.dart';

class LoginScreen extends ConsumerWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = GlobalKey<FormState>();
    final emailController = TextEditingController();
    final passwordController = TextEditingController();
    final obscurePassword = ValueNotifier<bool>(true);

    void login() async {
      if (!formKey.currentState!.validate()) return;

      try {
        await ref.read(authProvider.notifier).login(
              emailController.text.trim(),
              passwordController.text,
            );

        // Navigation will be handled by the auth state listener
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Login successful!')),
          );
        }
      } catch (e) {
        // Error is handled by the provider
      }
    }

    final authState = ref.watch(authProvider);

    return Scaffold(
      body: SafeArea(
        child: Stack(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 48),

                    // Logo/Title
                    Text(
                      'JobWise',
                      style: AppTextStyles.headlineLarge.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 8),

                    Text(
                      'AI-Powered Job Application Assistant',
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 64),

                    // Email field
                    TextFormField(
                      controller: emailController,
                      decoration: InputDecoration(
                        labelText: 'Email',
                        hintText: 'Enter your email',
                        prefixIcon: const Icon(Icons.email_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: AppColors.surface,
                      ),
                      keyboardType: TextInputType.emailAddress,
                      textInputAction: TextInputAction.next,
                      validator: Validators.validateEmail,
                      enabled: !authState.isLoading,
                    ),

                    const SizedBox(height: 16),

                    // Password field
                    ValueListenableBuilder<bool>(
                      valueListenable: obscurePassword,
                      builder: (context, isObscure, child) {
                        return TextFormField(
                          controller: passwordController,
                          decoration: InputDecoration(
                            labelText: 'Password',
                            hintText: 'Enter your password',
                            prefixIcon: const Icon(Icons.lock_outlined),
                            suffixIcon: IconButton(
                              icon: Icon(
                                isObscure
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                              onPressed: () {
                                obscurePassword.value = !isObscure;
                              },
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            filled: true,
                            fillColor: AppColors.surface,
                          ),
                          obscureText: isObscure,
                          textInputAction: TextInputAction.done,
                          validator: (value) {
                            if (value == null || value.isEmpty) {
                              return 'Password is required';
                            }
                            return null;
                          },
                          enabled: !authState.isLoading,
                          onFieldSubmitted: (_) => login(),
                        );
                      },
                    ),

                    const SizedBox(height: 24),

                    // Error display
                    if (authState.hasError && !authState.isLoading)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.error.withAlpha(25),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppColors.error.withAlpha(77)),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.error_outline,
                              color: AppColors.error,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                authState.error.toString(),
                                style: const TextStyle(color: AppColors.error),
                              ),
                            ),
                          ],
                        ),
                      ),

                    const SizedBox(height: 24),

                    // Login button
                    ElevatedButton(
                      onPressed: authState.isLoading ? null : login,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                      ),
                      child: Text(
                        authState.isLoading ? 'Signing in...' : 'Sign In',
                        style: AppTextStyles.button,
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Register link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          "Don't have an account? ",
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                        TextButton(
                          onPressed: authState.isLoading
                              ? null
                              : () {
                                  // Navigate to register screen
                                  Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (context) => const RegisterScreen(),
                                    ),
                                  );
                                },
                          child: const Text(
                            'Sign Up',
                            style: TextStyle(
                              color: AppColors.primary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 32),

                    // Forgot password link
                    Center(
                      child: TextButton(
                        onPressed: authState.isLoading
                            ? null
                            : () {
                                // TODO: Implement forgot password
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text('Forgot password feature coming soon!'),
                                  ),
                                );
                              },
                        child: const Text(
                          'Forgot Password?',
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Loading overlay
            if (authState.isLoading) const LoadingOverlay(),
          ],
        ),
      ),
    );
  }
}

class RegisterScreen extends ConsumerWidget {
  const RegisterScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = GlobalKey<FormState>();
    final emailController = TextEditingController();
    final passwordController = TextEditingController();
    final confirmPasswordController = TextEditingController();
    final fullNameController = TextEditingController();
    final obscurePassword = ValueNotifier<bool>(true);
    final obscureConfirmPassword = ValueNotifier<bool>(true);

    Future<void> register() async {
      if (!formKey.currentState!.validate()) return;

      try {
        await ref.read(authProvider.notifier).register(
              emailController.text.trim(),
              passwordController.text,
              fullNameController.text.trim(),
            );

        // Navigation will be handled by the auth state listener
        if (context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Account created successfully!')),
          );
        }
      } catch (e) {
        // Error is handled by the provider
      }
    }

    final authState = ref.watch(authProvider);

    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
          onPressed: authState.isLoading ? null : () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: Stack(
          children: [
            SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Form(
                key: formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const SizedBox(height: 24),

                    // Title
                    Text(
                      'Create Account',
                      style: AppTextStyles.headlineMedium.copyWith(
                        color: AppColors.textPrimary,
                        fontWeight: FontWeight.bold,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 8),

                    Text(
                      'Join JobWise to get started',
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: AppColors.textSecondary,
                      ),
                      textAlign: TextAlign.center,
                    ),

                    const SizedBox(height: 48),

                    // Full name field
                    TextFormField(
                      controller: fullNameController,
                      decoration: InputDecoration(
                        labelText: 'Full Name',
                        hintText: 'Enter your full name',
                        prefixIcon: const Icon(Icons.person_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: AppColors.surface,
                      ),
                      textInputAction: TextInputAction.next,
                      validator: Validators.validateFullName,
                      enabled: !authState.isLoading,
                    ),

                    const SizedBox(height: 16),

                    // Email field
                    TextFormField(
                      controller: emailController,
                      decoration: InputDecoration(
                        labelText: 'Email',
                        hintText: 'Enter your email',
                        prefixIcon: const Icon(Icons.email_outlined),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        filled: true,
                        fillColor: AppColors.surface,
                      ),
                      keyboardType: TextInputType.emailAddress,
                      textInputAction: TextInputAction.next,
                      validator: Validators.validateEmail,
                      enabled: !authState.isLoading,
                    ),

                    const SizedBox(height: 16),

                    // Password field
                    ValueListenableBuilder<bool>(
                      valueListenable: obscurePassword,
                      builder: (context, isObscure, child) {
                        return TextFormField(
                          controller: passwordController,
                          decoration: InputDecoration(
                            labelText: 'Password',
                            hintText: 'Enter your password',
                            prefixIcon: const Icon(Icons.lock_outlined),
                            suffixIcon: IconButton(
                              icon: Icon(
                                isObscure
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                              onPressed: () {
                                obscurePassword.value = !isObscure;
                              },
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            filled: true,
                            fillColor: AppColors.surface,
                          ),
                          obscureText: isObscure,
                          textInputAction: TextInputAction.next,
                          validator: Validators.validatePassword,
                          enabled: !authState.isLoading,
                        );
                      },
                    ),

                    const SizedBox(height: 16),

                    // Confirm password field
                    ValueListenableBuilder<bool>(
                      valueListenable: obscureConfirmPassword,
                      builder: (context, isObscure, child) {
                        return TextFormField(
                          controller: confirmPasswordController,
                          decoration: InputDecoration(
                            labelText: 'Confirm Password',
                            hintText: 'Re-enter your password',
                            prefixIcon: const Icon(Icons.lock_outlined),
                            suffixIcon: IconButton(
                              icon: Icon(
                                isObscure
                                    ? Icons.visibility_outlined
                                    : Icons.visibility_off_outlined,
                              ),
                              onPressed: () {
                                obscureConfirmPassword.value = !isObscure;
                              },
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                            filled: true,
                            fillColor: AppColors.surface,
                          ),
                          obscureText: isObscure,
                          textInputAction: TextInputAction.done,
                          validator: (value) =>
                              Validators.validateConfirmPassword(
                            value,
                            passwordController.text,
                          ),
                          enabled: !authState.isLoading,
                          onFieldSubmitted: (_) => register(),
                        );
                      },
                    ),

                    const SizedBox(height: 24),

                    // Error display
                    if (authState.hasError && !authState.isLoading)
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: AppColors.error.withAlpha(25),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: AppColors.error.withAlpha(77)),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.error_outline,
                              color: AppColors.error,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                authState.error.toString(),
                                style: const TextStyle(color: AppColors.error),
                              ),
                            ),
                          ],
                        ),
                      ),

                    const SizedBox(height: 24),

                    // Register button
                    ElevatedButton(
                      onPressed: authState.isLoading ? null : register,
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        backgroundColor: AppColors.primary,
                        foregroundColor: Colors.white,
                      ),
                      child: Text(
                        authState.isLoading ? 'Creating account...' : 'Create Account',
                        style: AppTextStyles.button,
                      ),
                    ),

                    const SizedBox(height: 16),

                    // Login link
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Text(
                          'Already have an account? ',
                          style: TextStyle(color: AppColors.textSecondary),
                        ),
                        TextButton(
                          onPressed: authState.isLoading
                              ? null
                              : () => Navigator.of(context).pop(),
                          child: const Text(
                            'Sign In',
                            style: TextStyle(
                              color: AppColors.primary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            // Loading overlay
            if (authState.isLoading) const LoadingOverlay(),
          ],
        ),
      ),
    );
  }
}