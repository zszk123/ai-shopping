from app.config import Settings


def test_generate_secret_is_long():
    assert len(Settings.generate_secret()) >= 32
