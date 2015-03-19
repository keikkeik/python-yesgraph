import pytest
from yesgraph import YesGraphAPI

from .data import entries, users


class Response:

    def __init__(self, status, *args, **kwargs):
        self.status = status

    def json(self):
        return {}

    def raise_for_status(self):
        pass

    @property
    def ok(self):
        return True


class DummySession:
    def request(self, method, *args, **kwargs):
        if method.lower() == 'get':
            return Response(status=200)

        if method.lower() == 'post':
            return Response(status=201)

        raise RuntimeError('Unexpected code path')


@pytest.fixture
def api():
    yg_api = YesGraphAPI('foo')
    yg_api.session = DummySession()
    return yg_api


def test_base_url():
    assert YesGraphAPI('foo').base_url == 'https://api.yesgraph.com/v0/'
    assert YesGraphAPI('foo', 'this_is_a_test').base_url == 'this_is_a_test'


def test_build_url(api):
    expected_url = 'foo/bar'
    assert api._build_url('foo', 'bar') == expected_url
    assert api._build_url('foo/', 'bar') == expected_url
    assert api._build_url('foo', '/bar') == expected_url


def test_build_json_in_request(api):
    with pytest.raises(TypeError):
        api._request('accidental json')


def test_test_endpoint(api):
    assert api.test() == {}


def test_get_address_book(api):
    assert api.get_address_book(1) == {}


def test_post_address_book(api):
    assert api.post_address_book(1, entries, 'Jonathan Chu', 'jonathan@yesgraph.com', 'gmail') == {}


def test_get_client_key(api):
    assert api.get_client_key(1) == {}


def test_post_invite_accepted(api):
    assert api.post_invite_accepted(42, 'john.smith@gmail.com', 'email', '2015-03-03T20:16:12+00:00') == {}


def test_post_invite_sent(api):
    assert api.post_invite_sent(42, 'john.smith@gmail.com', 'email', '2015-02-28T20:16:12+00:00') == {}


def test_get_users(api):
    assert api.get_users() == {}


def test_post_users(api):
    assert api.post_users(users) == {}
