from app.utils.response import fail, success


def test_success_shape():
    assert success({"hello": "world"}) == {"code": 200, "msg": "ok", "data": {"hello": "world"}}


def test_fail_shape():
    assert fail("bad", 400) == {"code": 400, "msg": "bad", "data": None}
