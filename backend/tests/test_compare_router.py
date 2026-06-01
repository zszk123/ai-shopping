from app.utils.image_validation import is_supported_image


def test_image_signature_allows_jpg_png_webp():
    assert is_supported_image(b"\xff\xd8\xffdemo")
    assert is_supported_image(b"\x89PNG\r\n\x1a\ndemo")
    assert is_supported_image(b"RIFFxxxxWEBPdemo")


def test_image_signature_rejects_non_image_bytes():
    assert not is_supported_image(b"not an image")
    assert not is_supported_image(b"")
