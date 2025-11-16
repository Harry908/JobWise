import 'package:dio/dio.dart';
import '../models/job.dart';

// A placeholder for your actual API client.
// You would replace the implementation with actual API calls.
class JobService {
  JobService(Dio dio);

  Future<List<Job>> getUserJobs({
    JobStatus? status,
    JobSource? source,
    int page = 1,
    int limit = 20,
  }) async {
    // Simulate network delay
    await Future.delayed(const Duration(milliseconds: 500));

    // In a real app, you'd make a network request:
    // final response = await _dio.get('/user/jobs', queryParameters: {
    //   'status': status?.name,
    //   'source': source?.name,
    //   'page': page,
    //   'limit': limit,
    // });
    // return (response.data['jobs'] as List).map((json) => Job.fromJson(json)).toList();

    // For now, return mock data
    // print(
    //     'Fetching jobs... page: $page, status: $status, source: $source');
    return _generateMockJobs(page, limit);
  }

  Future<Job> getJobById(String id) async {
    await Future.delayed(const Duration(milliseconds: 300));
    return _generateMockJobs(1, 1).first.copyWith(id: id);
  }

  Future<Job> createJob(Job job) async {
    await Future.delayed(const Duration(milliseconds: 400));
    // final response = await _dio.post('/jobs', data: job.toJson());
    // return Job.fromJson(response.data);
    return job.copyWith(id: DateTime.now().millisecondsSinceEpoch.toString());
  }

  Future<Job> updateJob(Job job) async {
    await Future.delayed(const Duration(milliseconds: 400));
    // final response = await _dio.put('/jobs/${job.id}', data: job.toJson());
    // return Job.fromJson(response.data);
    return job;
  }

  Future<void> deleteJob(String id) async {
    await Future.delayed(const Duration(milliseconds: 600));
    // await _dio.delete('/jobs/$id');
    // print('Deleted job $id');
  }

  Future<List<BrowseJob>> browseJobs(
      {String? query, String? location, bool? remote, int page = 1, int limit = 20}) async {
    await Future.delayed(const Duration(milliseconds: 800));
    // final response = await _dio.get('/browse/jobs', queryParameters: {'page': page, 'limit': limit});
    // return (response.data['jobs'] as List).map((json) => BrowseJob.fromJson(json)).toList();
    return List.generate(
      limit,
      (index) => BrowseJob(
        id: 'browse_${page}_$index',
        source: JobSource.mock,
        title: 'Mock Browse Job ${page * limit + index}',
        company: 'Mock Company',
        location: 'Remote',
        description: 'This is a mock job description for a browsed job.',
      ),
    );
  }

  // Helper to generate mock jobs for demonstration
  List<Job> _generateMockJobs(int page, int limit) {
    if (page > 3) return []; // Simulate end of list
    return List.generate(
      limit,
      (index) {
        final id = 'mock_${page}_$index';
        final now = DateTime.now();
        return Job(
          id: id,
          title: 'Software Engineer ${page * limit + index}',
          company: 'Tech Solutions Inc.',
          description:
              'Developing next-gen applications. Need experience with Dart and Flutter.',
          source: JobSource.mock,
          status: JobStatus.active,
          applicationStatus: ApplicationStatus.notApplied,
          createdAt: now,
          updatedAt: now,
        );
      },
    );
  }
}
