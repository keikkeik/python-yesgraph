import pytest
from yesgraph import YesGraphAPI

from .data import entries, users


class DummySession:
    def request(self, method, *args, **kwargs):
        raise RuntimeError('You should not be making actual requests from the test suite!')


@pytest.fixture
def api():
    yg_api = YesGraphAPI('foo')
    yg_api.session = DummySession()
    return yg_api


def test_base_url():
    assert YesGraphAPI('foo').base_url == 'https://api.yesgraph.com/v0/'
    assert YesGraphAPI('foo', 'this_is_a_test').base_url == 'this_is_a_test'



@pytest.mark.xfail
def test_build_url(api):
    expected_url = 'foo/bar'
    assert api._build_url('foo', 'bar') == expected_url
    assert api._build_url('foo/', 'bar') == expected_url
    assert api._build_url('foo', '/bar') == expected_url


@pytest.mark.xfail
def test_build_json_in_request(api):
    with pytest.raises(TypeError):
        api._request('accidental json')


@pytest.mark.xfail
def test_test_endpoint(api):
    assert api.test() == {}


@pytest.mark.xfail
def test_get_address_book(api):
    assert api.get_address_book(1) == {}


@pytest.mark.xfail
def test_post_address_book(api):
    assert api.post_address_book(1, entries, 'Jonathan Chu', 'jonathan@yesgraph.com', 'gmail') == {}


@pytest.mark.xfail
def test_get_client_key(api):
    assert api.get_client_key(1) == {}


@pytest.mark.xfail
def test_post_invite_accepted(api):
    assert api.post_invite_accepted(42, 'john.smith@gmail.com', 'email', '2015-03-03T20:16:12+00:00') == {}


@pytest.mark.xfail
def test_post_invite_sent(api):
    assert api.post_invite_sent(42, 'john.smith@gmail.com', 'email', '2015-02-28T20:16:12+00:00') == {}


@pytest.mark.xfail
def test_get_users(api):
    assert api.get_users() == {}


@pytest.mark.xfail
def test_post_users(api):
    assert api.post_users(users) == {}
