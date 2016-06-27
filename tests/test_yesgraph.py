import json
from datetime import datetime

from requests import HTTPError

import pytest
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


def test_user_agent(api):
    req = api._request('GET', '/foo')  # any GET request
    user_agent = req.headers['User-Agent']

    # Test User Agent consists of 3 parts (client, language, platform)
    client_info, lang_info, platform_info = user_agent.split(' ')

    client, _ = client_info.split('/')
    assert client == 'python-yesgraph'

    # We don't want to be testing too much here, since the tests can be run
    # from anywhere
    _, _ = lang_info.split('/')
    _, _ = platform_info.split('/')


def test_endpoint_test(api):
    req = api.test()
    assert req.method == 'GET'
    assert req.url == 'https://api.yesgraph.com/v0/test'
    assert req.body is None


def test_endpoint_get_client_key(api):
    req = api._get_client_key(user_id=1234)
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/client-key'
    assert req.body == 'user_id=1234'


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
    req = api.post_address_book(user_id=1234, entries=ENTRIES, source_type='gmail', limit=20)
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/address-book'

    assert json.loads(req.body) == {
        'user_id': '1234',
        'source': {'type': 'gmail'},
        'filter_suggested_seen': None,
        'filter_existing_users': None,
        'filter_invites_sent': None,
        'promote_existing_users': None,
        'entries': ENTRIES,
        'limit': 20
    }

    req = api.post_address_book(user_id=1234, entries=ENTRIES, source_type='gmail',
                                filter_suggested_seen=1, limit=20)
    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/address-book'

    assert json.loads(req.body) == {
        'user_id': '1234',
        'source': {'type': 'gmail'},
        'filter_suggested_seen': 1,
        'filter_existing_users': None,
        'filter_invites_sent': None,
        'promote_existing_users': None,
        'entries': ENTRIES,
        'limit': 20
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
        'filter_suggested_seen': None,
        'filter_existing_users': None,
        'filter_invites_sent': None,
        'promote_existing_users': None,
        'entries': ENTRIES,
        'limit': None
    }


def test_endpoint_post_suggested_seen(api):
    entries = [
        {'user_id': '1229',
         'name': 'John Doe',
         'phones': ['+1 4442223333', '+1 555-222-1234'],
         'seen_at': '2015-03-28T20:16:12+00:00'
         },
        {'user_id': '1234',
         'name': 'Jean Doe',
         'emails': ['abigail.kirigin@gmail.com'],
         'seen_at': '2015-03-28T20:16:12+00:00'
         },
        {'user_id': '5678',
         'name': 'Jane Doe',
         'phones': ['+1 555 222 3333', '+1 555 222 3331'],
         'seen_at':'2015-02-28T20:16:12+00:00'
         },
        {'user_id': '5678',
         'phones': ['+1 555-999-1234'],
         'seen_at': '2015-01-28T20:16:12+00:00'
         }
    ]

    req = api.post_suggested_seen(entries=entries)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/suggested-seen'
    assert json.loads(req.body) == {'entries': entries}


def test_endpoint_post_invites_sent(api):
    entries = [
        {'user_id': '1229',
         'invitee_name': 'John Doe',
         'phone': '+1 555 222 3333',
         'sent_at': '2015-03-28T20:16:12+00:00'
         },
        {'user_id': '1234',
         'invitee_name': 'Jane Doe',
         'email': 'jane@yesgraph.com',
         'phone': '+1 555 222 2222',
         'sent_at': '2015-03-28T20:16:12+00:00'
         },
        {'user_id': '5678',
         'invitee_name': 'Jean Doe',
         'phone': '+1 555 222 1111',
         'sent_at': '2015-02-28T20:16:12+00:00'
         },
        {'user_id': '5678',
         'phone': '+1 555 222 5555',
         'sent_at': '2015-01-28T20:16:12+00:00'
         }
    ]

    req = api.post_invites_sent(entries=entries)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/invites-sent'
    assert json.loads(req.body) == {'entries': entries}


def test_endpoint_post_invites_accepted(api):
    entries = [
        {'new_user_id': '1229',
         'name': 'John Doe',
         'phone': '+1 555 222 3333',
         'accepted_at': '2015-03-28T20:16:12+00:00'
         },
        {'new_user_id': '1234',
         'name': 'Jane Doe',
         'email': 'jane@yesgraph.com',
         'phone': '+1 555 222 2222',
         'accepted_at': '2015-03-28T20:16:12+00:00'
         },
        {'new_user_id': '5678',
         'name': 'Jean Doe',
         'phone': '+1 555 222 1111',
         'accepted_at': '2015-02-28T20:16:12+00:00'
         },
        {'new_user_id': '5678',
         'phone': '+1 555 222 5555',
         'accepted_at': '2015-01-28T20:16:12+00:00'
         }
    ]

    req = api.post_invites_accepted(entries=entries)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/invites-accepted'

    assert json.loads(req.body) == {'entries': entries}


def test_endpoint_post_users(api):
    USERS = {'entries': [
        {'id': 1, 'name': 'John Smith', 'email': 'john.smith@gmail.com'},
        {'id': 2, 'name': 'Jane Doe', 'email': 'jane.doe@gmail.com'},
    ]}

    req = api.post_users(USERS)

    assert req.method == 'POST'
    assert req.url == 'https://api.yesgraph.com/v0/users'

    assert json.loads(req.body) == USERS


def test_endpoint_get_followers(api):
    user_id = "1234"
    email = "email@email.com"
    phone = "555-111-2222"

    req = api.get_followers(type_name='user_id', identifier=user_id)
    assert req.url == 'https://api.yesgraph.com/v0/followers/{0}/{1}'.format('user_id', user_id)
    req = api.get_followers(type_name='email', identifier=email)
    assert req.url == 'https://api.yesgraph.com/v0/followers/{0}/{1}'.format('email', email)
    req = api.get_followers(type_name='phone', identifier=phone)
    assert req.url == 'https://api.yesgraph.com/v0/followers/{0}/{1}'.format('phone', phone)
    assert req.method == 'GET'


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
