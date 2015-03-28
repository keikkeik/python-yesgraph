import json
from datetime import datetime

import pytest
from requests import HTTPError
from yesgraph import YesGraphAPI

from .helpers import make_fake_response


class SafeYesGraphAPI(YesGraphAPI):
    def _request(self, method, endpoint, data=None, **url_args):
        """
        Safe version of the `_request()` call that does not actually send
        the request, but just returns the PreparedRequest instance, for
        inspection.
        """
        prepped_req = self._prepare_request(method, endpoint, data=data, **url_args)
        return prepped_req


@pytest.fixture
def api():
    return SafeYesGraphAPI(secret_key='foo')


def test_build_url(api):
    assert api._build_url('foo') == 'https://api.yesgraph.com/v0/foo'
    assert api._build_url('foo/bar') == 'https://api.yesgraph.com/v0/foo/bar'
    assert api._build_url('/test') == 'https://api.yesgraph.com/v0/test'
    assert api._build_url('test') == 'https://api.yesgraph.com/v0/test'
    assert api._build_url('test', foo=3) == 'https://api.yesgraph.com/v0/test?foo=3'
    assert api._build_url('test', bar='foo', qux=None) == 'https://api.yesgraph.com/v0/test?bar=foo'


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

    req = api._request('GET', '/any/url/really')
    assert req.headers['Authorization'] == 'Bearer the-s3cr3t-key'

    req = api._request('POST', '/any/url/really')
    assert req.headers['Authorization'] == 'Bearer the-s3cr3t-key'


def test_content_type(api):
    req = api._request('GET', '/foo')  # any GET request
    assert req.headers['Content-Type'] == 'application/json'

    req = api._request('POST', '/foo')  # any POST request
    assert req.headers['Content-Type'] == 'application/json'


def test_endpoint_test(api):
    req = api.test()
    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/test'
    assert req.body is None


def test_endpoint_get_client_key(api):
    req = api._get_client_key(user_id=1234)
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/client-key'
    assert req.body == '{"user_id": "1234"}'


def test_endpoint_get_address_book(api):
    req = api.get_address_book(user_id=1234)
    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/address-book/1234'
    assert req.body is None

    # Test URL unsafe arguments to methods
    req = api.get_address_book(user_id='user/with?unsafe&chars=inthem')
    assert req.url == 'https://api.yesgraph.com/v0/address-book/user%2Fwith%3Funsafe%26chars%3Dinthem'


def test_endpoint_post_address_book(api):
    # Simplest invocation (without source info)
    ENTRIES = [
        {'name': 'Foo', 'email': 'foo@example.org'},
        {'name': 'Bar', 'email': 'bar@example.org'},
    ]
    req = api.post_address_book(user_id=1234, entries=ENTRIES, source_type='gmail')
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/address-book'

    assert json.loads(req.body) == {
        'user_id': '1234',
        'source': {'type': 'gmail'},
        'entries': ENTRIES,
    }


def test_endpoint_post_address_book_with_source_info(api):
    # Invocation with source info
    ENTRIES = [
        {'name': 'Foo', 'email': 'foo@example.org'},
    ]
    req = api.post_address_book(user_id=1234, entries=ENTRIES,
                                source_type='ios', source_name='Mr. Test',
                                source_email='test@example.org')
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/address-book'

    assert json.loads(req.body) == {
        'user_id': '1234',
        'source': {'type': 'ios', 'name': 'Mr. Test', 'email': 'test@example.org'},
        'entries': ENTRIES,
    }


def test_endpoint_post_invite_sent(api):
    # Simplest invocation
    req = api.post_invite_sent(user_id=42, invitee_id='john.smith@gmail.com')

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/invite-sent'

    assert json.loads(req.body) == {
        'user_id': '42',
        'invitee_type': 'email',
        'invitee_id': 'john.smith@gmail.com',
    }


def test_endpoint_post_invite_sent_advanced(api):
    # Invocation with advanced (optional params)
    now = datetime(2015, 3, 19, 13, 37, 00)
    req = api.post_invite_sent(user_id=1234, invitee_id='555-123000',
                               invitee_type='phone', sent_at=now)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/invite-sent'

    assert json.loads(req.body) == {
        'sent_at': '2015-03-19T13:37:00',
        'user_id': '1234',
        'invitee_type': 'phone',
        'invitee_id': '555-123000',
    }


def test_endpoint_post_invite_accepted(api):
    # Simplest invocation
    req = api.post_invite_accepted('john.smith@gmail.com')

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/invite-accepted'

    assert json.loads(req.body) == {
        'invitee_type': 'email',
        'invitee_id': 'john.smith@gmail.com',
    }


def test_endpoint_post_invite_accepted_advanced(api):
    # Invocation with advanced (optional params)
    now = datetime(2015, 3, 19, 13, 37, 00)
    req = api.post_invite_accepted('555-123000', invitee_type='phone',
                                   accepted_at=now, new_user_id=42)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/invite-accepted'

    assert json.loads(req.body) == {
        'accepted_at': '2015-03-19T13:37:00',
        'invitee_type': 'phone',
        'invitee_id': '555-123000',
        'new_user_id': '42',
    }


def test_endpoint_get_users(api):
    req = api.get_users()

    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/users'
    assert req.body is None


def test_endpoint_post_users(api):
    USERS = [
        {'id': 1, 'name': 'John Smith', 'email': 'john.smith@gmail.com'},
        {'id': 2, 'name': 'Jane Doe', 'email': 'jane.doe@gmail.com'},
    ]

    req = api.post_users(USERS)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/users'
    assert json.loads(req.body) == USERS


def test_response_success(api):
    fake_http_response = make_fake_response(200, {
        'meta': {
            # ...
        },
        'data': [
            # ...
        ],
    })
    result = api._handle_response(fake_http_response)
    assert 'meta' in result
    assert 'data' in result


def test_response_with_error(api):
    fake_http_response = make_fake_response(404, {
        'error': 'not found',
    })

    with pytest.raises(HTTPError):
        api._handle_response(fake_http_response)


def test_endpoint_get_address_books(api):
    req = api.get_address_books()
    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/address-books'
    assert req.body is None


def test_endpoint_get_facebook(api):
    req = api.get_facebook(user_id=1234)
    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/facebook/1234'
    assert req.body is None

    # Test URL unsafe arguments to methods
    req = api.get_facebook(user_id='user/with?unsafe&chars=inthem')
    assert req.url == 'https://api.yesgraph.com/v0/facebook/user%2Fwith%3Funsafe%26chars%3Dinthem'


def test_endpoint_post_facebook(api):
    # Simplest invocation (without user_id info)
    FRIENDS = [
        {"id": "10000012345", "name": "John Doe"},
        {"id": "10000012389", "name": "Jane Borger"},
    ]
    req = api.post_facebook(friends=FRIENDS, source_id=1234)
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/facebook'

    assert json.loads(req.body) == {
        'self': {'id': 1234},
        'friends': FRIENDS,
    }


def test_endpoint_post_google(api):
    sentinel = {'dummy': 'payload'}

    req = api.post_google(user_id=1234, payload=sentinel, source_type='gmail')
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/google'

    assert json.loads(req.body) == {
        'user_id': '1234',
        'source': {'type': 'gmail'},
        'payload': sentinel,
    }
