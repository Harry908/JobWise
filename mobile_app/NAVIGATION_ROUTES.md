# JobWise Mobile App - Navigation Routes

## Route Structure

### Authentication Routes
- `/login` - Login screen
- `/register` - Registration screen

### Main Routes
- `/home` - Home screen with navigation buttons

### Profile Routes
- `/profile/view` - View profile details
- `/profile/edit` - Create/edit profile

### Job Routes ✨ **NEW**
- `/jobs` - List of user's saved jobs (JobListScreen)
- `/jobs/paste` - Paste raw job text for parsing (JobPasteScreen)
- `/jobs/browse` - Browse mock job listings (JobBrowseScreen)
- `/jobs/:id` - Job detail view with edit/delete actions (JobDetailScreen)

### Utility Routes
- `/settings` - App settings
- `/debug` - Debug tools (token management, etc.)

---

## Navigation Patterns

### From HomeScreen
```dart
// Navigate to saved jobs list
context.push('/jobs');

// Navigate to browse mock jobs
context.push('/jobs/browse');

// Navigate to profile view
context.push('/profile/view');

// Navigate to profile edit
context.push('/profile/edit');
```

### Job Feature Navigation
```dart
// From JobListScreen floating action button
context.push('/jobs/paste');  // Paste job text
context.push('/jobs/browse'); // Browse mock jobs

// From JobListScreen or JobBrowseScreen (tap on job card)
context.push('/jobs/$jobId');

// From JobDetailScreen (edit button)
context.push('/jobs/$jobId/edit'); // TODO: Implement edit screen
```

### Back Navigation
```dart
// Return to previous screen
context.pop();

// Return with result
context.pop(result);
```

---

## Route Parameters

### Dynamic Job ID
The `/jobs/:id` route uses a path parameter to pass the job ID:

```dart
GoRoute(
  path: '/jobs/:id',
  builder: (context, state) {
    final jobId = state.pathParameters['id']!;
    return JobDetailScreen(jobId: jobId);
  },
),
```

---

## Authentication Guards

The app uses redirect logic to enforce authentication:

```dart
redirect: (context, state) {
  final authState = ref.read(authProvider);
  final isLoggedIn = authState.isAuthenticated;
  final isLoggingIn = state.matchedLocation == '/login';
  final isRegistering = state.matchedLocation == '/register';

  // Redirect to login if not authenticated
  if (!isLoggedIn && !isLoggingIn && !isRegistering) {
    return '/login';
  }

  // Redirect to home if already logged in
  if (isLoggedIn && (isLoggingIn || isRegistering)) {
    return '/home';
  }

  return null; // No redirect needed
}
```

---

## Pending Routes

### To Be Implemented
- `/jobs/:id/edit` - Edit job details (JobEditScreen)
- `/generations` - List of resume generations
- `/generations/:id` - Generation progress/result
- `/documents` - Document library
- `/documents/:id` - Document viewer

---

## Testing Routes

To test navigation in the app:

1. **Start the app** - Should redirect to `/login`
2. **After login** - Redirects to `/home`
3. **From home** - Click "My Jobs" → `/jobs`
4. **From home** - Click "Browse Jobs" → `/jobs/browse`
5. **From job list** - Tap job card → `/jobs/:id`
6. **From browse** - Tap job card → Opens detail modal
7. **From browse modal** - Click "Save Job" → Creates job and navigates to detail

---

## HomeScreen Features

The HomeScreen now includes job navigation when user has a profile:

```dart
if (profileState.profile != null) {
  // My Jobs button (primary action)
  ElevatedButton.icon(
    onPressed: () => context.push('/jobs'),
    icon: const Icon(Icons.work),
    label: const Text('My Jobs'),
  ),
  
  // Browse Jobs button (secondary action)
  OutlinedButton.icon(
    onPressed: () => context.push('/jobs/browse'),
    icon: const Icon(Icons.search),
    label: const Text('Browse Jobs'),
  ),
  
  // Profile buttons
  // ...
}
```

Users without profiles only see the "Create Profile" button.

---

## Integration with Backend

All job screens integrate with the backend API at:
- **Base URL**: `http://10.0.2.2:8000` (Android) or `http://localhost:8000` (iOS)
- **API Prefix**: `/api/v1`
- **Job Endpoints**: `/api/v1/jobs/*`

Make sure the backend server is running before testing job features.
