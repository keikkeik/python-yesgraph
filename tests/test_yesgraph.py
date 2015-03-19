import pytest
from yesgraph import YesGraphAPI

from .data import entries, users


class SafeYesGraphAPI(YesGraphAPI):
    def _request(self, method, endpoint, data=None):
        """
        Safe version of the `_request()` call that does not actually send
        the request, but just returns the PreparedRequest instance, for
        inspection.
        """
        prepped_req = self._prepare_request(method, endpoint, data=data)
        return prepped_req


@pytest.fixture
def api():
    return SafeYesGraphAPI(secret_key='foo')


def test_build_url(api):
    assert api._build_url('foo') == 'https://api.yesgraph.com/v0/foo'
    assert api._build_url('foo/bar') == 'https://api.yesgraph.com/v0/foo/bar'
    assert api._build_url('/test') == 'https://api.yesgraph.com/v0/test'
    assert api._build_url('test') == 'https://api.yesgraph.com/v0/test'


def test_base_url(api):
    # Default base URL
    assert api.base_url == 'https://api.yesgraph.com/v0/'

    req = api._prepare_request('GET', '/test')
    assert req.url == 'https://api.yesgraph.com/v0/test'

    # Custom base URL
    api = SafeYesGraphAPI(secret_key='dummy', base_url='http://www.example.org')
    assert api.base_url == 'http://www.example.org'

    # Test base URL ends up in requests
    req = api._prepare_request('GET', '/test')
    assert req.url == 'http://www.example.org/test'


def test_secret_key(api):
    api.secret_key = 'the-s3cr3t-key'
    req = api.test()  # could be _any_ request
    assert req.headers['Authorization'] == 'Bearer the-s3cr3t-key'


def test_endpoint_test(api):
    req = api.test()
    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/test'
    assert 'Authorization' in req.headers
    assert req.body is None


@pytest.mark.xfail
def test_endpoint_get_client_key(api):
    assert api.get_client_key(1) == {}


@pytest.mark.xfail
def test_endpoint_get_address_book(api):
    assert api.get_address_book(1) == {}


@pytest.mark.xfail
def test_endpoint_post_address_book(api):
    assert api.post_address_book(1, entries, 'Jonathan Chu', 'jonathan@yesgraph.com', 'gmail') == {}


@pytest.mark.xfail
def test_endpoint_post_invite_accepted(api):
    assert api.post_invite_accepted(42, 'john.smith@gmail.com', 'email', '2015-03-03T20:16:12+00:00') == {}


@pytest.mark.xfail
def test_endpoint_post_invite_sent(api):
    assert api.post_invite_sent(42, 'john.smith@gmail.com', 'email', '2015-02-28T20:16:12+00:00') == {}


@pytest.mark.xfail
def test_endpoint_get_users(api):
    assert api.get_users() == {}


@pytest.mark.xfail
def test_endpoint_post_users(api):
    assert api.post_users(users) == {}
