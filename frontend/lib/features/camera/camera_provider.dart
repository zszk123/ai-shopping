import 'dart:typed_data';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';

enum CameraStatus { idle, picking, done }

class CameraState {
  final CameraStatus status;
  final Uint8List? imageBytes;

  const CameraState({this.status = CameraStatus.idle, this.imageBytes});

  CameraState copyWith({
    CameraStatus? status,
    Uint8List? imageBytes,
    bool clearImageBytes = false,
  }) {
    return CameraState(
      status: status ?? this.status,
      imageBytes: clearImageBytes ? null : imageBytes ?? this.imageBytes,
    );
  }
}

class CameraNotifier extends StateNotifier<CameraState> {
  final ImagePicker _picker = ImagePicker();

  CameraNotifier() : super(const CameraState());

  Future<Uint8List?> pickFromGallery() async {
    state = const CameraState(status: CameraStatus.picking);
    final xfile =
        await _picker.pickImage(source: ImageSource.gallery, imageQuality: 85);
    if (xfile == null) {
      state = const CameraState();
      return null;
    }
    return _processImage(xfile);
  }

  Future<Uint8List?> takePhoto() async {
    state = const CameraState(status: CameraStatus.picking);
    final xfile =
        await _picker.pickImage(source: ImageSource.camera, imageQuality: 85);
    if (xfile == null) {
      state = const CameraState();
      return null;
    }
    return _processImage(xfile);
  }

  Future<Uint8List?> _processImage(XFile xfile) async {
    state = state.copyWith(status: CameraStatus.picking);
    try {
      final bytes = await xfile.readAsBytes();
      state = state.copyWith(status: CameraStatus.done, imageBytes: bytes);
      return bytes;
    } catch (e) {
      state = state.copyWith(status: CameraStatus.idle);
      return null;
    }
  }

  void reset() {
    state = const CameraState();
  }
}

final cameraProvider =
    StateNotifierProvider<CameraNotifier, CameraState>((ref) {
  return CameraNotifier();
});
