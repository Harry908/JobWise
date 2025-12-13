// Stub file for conditional imports
// This file provides stub implementations when the actual libraries aren't available

// Stub for dart:html types on non-web platforms
class Blob {
  Blob(List<dynamic> parts, [String? type]);
}

class Url {
  static String createObjectUrlFromBlob(Blob blob) => '';
  static void revokeObjectUrl(String url) {}
}

class AnchorElement {
  String? href;
  String? download;
  CssStyleDeclaration get style => CssStyleDeclaration();
  void click() {}
  void remove() {}
}

class CssStyleDeclaration {
  String display = '';
}

class HtmlDocument {
  BodyElement? body;
}

class BodyElement {
  void append(dynamic element) {}
}

HtmlDocument get document => HtmlDocument();

// Stub for dart:io types on web platforms
class File {
  final String path;
  File(this.path);
  Future<bool> exists() async => false;
  Future<List<int>> readAsBytes() async => [];
  Future<File> writeAsBytes(List<int> bytes) async => this;
}

class Directory {
  final String path;
  Directory(this.path);
  Future<bool> exists() async => false;
  Future<Directory> create({bool recursive = false}) async => this;
}

// Stub for path_provider on web
Future<Directory> getApplicationDocumentsDirectory() async => Directory('');
