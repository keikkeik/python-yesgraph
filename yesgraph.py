import platform
from collections import Iterable
from datetime import datetime

import six
from requests import Request, Session

from six.moves.urllib.parse import quote_plus

__version__ = '0.4.2'


def is_nonstring_iterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, six.string_types)


def format_date(obj):
    if isinstance(obj, (int, six.string_types)):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        raise TypeError('Cannot format {0} as a date.'.format(obj))  # pragma: no cover


class YesGraphAPI(object):
    def __init__(self, secret_key, base_url='https://api.yesgraph.com/v0/'):
        self.secret_key = secret_key
        self.base_url = base_url
        self.session = Session()

    @property
    def user_agent(self):
        client_info = '/'.join(('python-yesgraph', __version__))
        language_info = '/'.join((platform.python_implementation(), platform.python_version()))
        platform_info = '/'.join((platform.system(), platform.release()))
        return ' '.join([client_info, language_info, platform_info])

    def _build_url(self, endpoint, **url_args):
        url = '/'.join((self.base_url.rstrip('/'), endpoint.lstrip('/')))

        clean_args = dict((k, v) for k, v in url_args.items() if v is not None)
        if clean_args:
            args = six.moves.urllib.parse.urlencode(clean_args)
            url = '{0}?{1}'.format(url, args)

        return url

    def _prepare_request(self, method, endpoint, data=None, limit=None):
        """Builds and prepares the complete request, but does not send it."""
        headers = {
            'Authorization': 'Bearer {0}'.format(self.secret_key),
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent,
        }

        url = self._build_url(endpoint, limit=limit)

        # Prepare the data
        if data is not None:
            if not is_nonstring_iterable(data):
                msg = 'Argument "data" must be (non-string) iterable, got: {0!r}'
                raise TypeError(msg.format(data))  # pragma: no cover  # noqa

        req = Request(method, url, json=data, headers=headers)
        prepped_req = self.session.prepare_request(req)
        return prepped_req

    def _request(self, method, endpoint, data=None, **url_args):  # pragma: no cover
        """
        Builds, prepares, and sends the complete request to the YesGraph API,
        returning the decoded response.
        """
        prepped_req = self._prepare_request(method, endpoint, data=data, **url_args)
        resp = self.session.send(prepped_req)
        return self._handle_response(resp)

    def _handle_response(self, response):
        """Decodes the HTTP response when successful, or throws an error."""
        response.raise_for_status()
        return response.json()

    def test(self):
        """
        Wrapped method for GET of /test endpoint

        Documentation - https://www.yesgraph.com/docs/reference#get-test
        """
        return self._request('GET', '/test')

    def _get_client_key(self, user_id):
        return self._request('POST', '/client-key', {'user_id': str(user_id)})

    def get_client_key(self, user_id):
        """
        Wrapped method for POST of /client-key endpoint

        Documentation - https://www.yesgraph.com/docs/reference#obtaining-a-client-api-key
        """
        result = self._get_client_key(user_id)
        return result['client_key']

    def get_address_book(self, user_id, limit=None):
        """
        Wrapped method for GET of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/reference#get-address-bookuser_id
        """
        endpoint = '/address-book/{0}'.format(quote_plus(str(user_id)))
        return self._request('GET', endpoint, limit=limit)

    def post_address_book(self, user_id, entries,
                          source_type, source_name=None, source_email=None):
        """
        Wrapped method for POST of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-address-book
        """
        source = {
            'type': source_type,
        }
        if source_name:
            source['name'] = source_name
        if source_email:
            source['email'] = source_email

        data = {
            'user_id': str(user_id),
            'source': source,
            'entries': entries,
        }
        return self._request('POST', '/address-book', data)

    def post_invite_accepted(self, invitee_id, invitee_type='email',
                             accepted_at=None, new_user_id=None):
        """
        Wrapped method for POST of /invite-accepted endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-invite-accepted
        """
        data = {
            'invitee_id': str(invitee_id),
            'invitee_type': invitee_type,
        }
        if accepted_at:
            data['accepted_at'] = format_date(accepted_at)
        if new_user_id:
            data['new_user_id'] = str(new_user_id)

        return self._request('POST', '/invite-accepted', data)

    def post_invite_sent(self, user_id, invitee_id, invitee_type='email', sent_at=None):
        """
        Wrapped method for POST of /invite-sent endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-invite-sent
        """
        data = {
            'user_id': str(user_id),
            'invitee_id': str(invitee_id),
            'invitee_type': invitee_type,
        }
        if sent_at:
            data['sent_at'] = format_date(sent_at)

        return self._request('POST', '/invite-sent', data)

    def get_users(self):
        """
        Wrapped method for GET of /users endpoint

        Documentation - https://www.yesgraph.com/docs/reference#get-users
        """
        return self._request('GET', '/users')

    def post_users(self, users):
        """
        Wrapped method for POST of users endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-users
        """
        return self._request('POST', '/users', users)

    def get_address_books(self, limit=None):
        """
        Wrapped method for GET of /address-books endpoint

        Documentation - https://www.yesgraph.com/docs/reference#get-address-books
        """
        return self._request('GET', '/address-books', limit=limit)

    def post_facebook(self, friends, user_id=None, source_id=None,
                      source_name=None):
        """
        Wrapped method for POST of /facebook endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-facebook
        """
        source = {}
        if source_id:
            source['id'] = source_id
        if source_name:
            source['name'] = source_name

        data = {
            'self': source,
            'friends': friends,
        }

        if user_id:
            data['user_id'] = user_id

        return self._request('POST', '/facebook', data)

    def get_facebook(self, user_id):
        """
        Wrapped method for GET of /facebook endpoint

        Documentation - https://www.yesgraph.com/docs/reference#get-facebookuser_id
        """
        return self._request('GET', '/facebook/{0}'.format(quote_plus(str(user_id))))
