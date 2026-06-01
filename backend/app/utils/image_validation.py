MAX_IMAGE_SIZE = 8 * 1024 * 1024


def is_supported_image(file_bytes: bytes) -> bool:
    if not file_bytes:
        return False
    if file_bytes.startswith(b"RIFF"):
        return len(file_bytes) > 12 and file_bytes[8:12] == b"WEBP"
    return file_bytes.startswith(b"\xff\xd8\xff") or file_bytes.startswith(b"\x89PNG\r\n\x1a\n")
