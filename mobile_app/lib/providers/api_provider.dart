import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

part 'api_provider.g.dart';

@riverpod
Dio dio(Ref ref) {
  return Dio();
}
