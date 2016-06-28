import platform
from datetime import datetime
import json

import six
from requests import Request, Session

from six.moves.urllib.parse import quote_plus

__version__ = '0.6.0'


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

    def _prepare_request(self, method, endpoint, data=None,
                         filter_suggested_seen=None,
                         filter_existing_users=None,
                         filter_invites_sent=None,
                         promote_existing_users=None, limit=None):
        """Builds and prepares the complete request, but does not send it."""
        headers = {
            'Authorization': 'Bearer {0}'.format(self.secret_key),
            'Content-Type': 'application/json',
            'User-Agent': self.user_agent,
        }

        url = self._build_url(endpoint, filter_suggested_seen=filter_suggested_seen,
                              filter_existing_users=filter_existing_users,
                              filter_invites_sent=filter_invites_sent,
                              promote_existing_users=promote_existing_users,
                              limit=limit)

        req = Request(method, url, data=data, headers=headers)

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

        Documentation - https://www.yesgraph.com/docs/test
        """
        return self._request('GET', '/test')

    def _get_client_key(self, user_id):
        return self._request('POST', '/client-key', {'user_id': str(user_id)})

    def get_client_key(self, user_id):
        """
        Wrapped method for POST of /client-key endpoint

        Documentation - https://docs.yesgraph.com/docs/create-client-keys
        """
        result = self._get_client_key(user_id)
        return result['client_key']

    def get_address_book(self, user_id, filter_suggested_seen=None,
                         filter_existing_users=None,
                         filter_invites_sent=None,
                         promote_existing_users=None, limit=None):
        """
        Wrapped method for GET of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/address-book
        """

        urlargs = {'filter_suggested_seen': filter_suggested_seen,
                   'filter_existing_users': filter_existing_users,
                   'filter_invites_sent': filter_invites_sent,
                   'promote_existing_users': promote_existing_users,
                   'limit': limit}

        endpoint = '/address-book/{0}'.format(quote_plus(str(user_id)))
        return self._request('GET', endpoint, **urlargs)

    def post_address_book(self, user_id, entries, source_type, source_name=None,
                          source_email=None, filter_suggested_seen=None,
                          filter_existing_users=None,
                          filter_invites_sent=None,
                          promote_existing_users=None, limit=None):
        """
        Wrapped method for POST of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/address-book
        """
        source = {
            'type': source_type,
        }
        if source_name:
            source['name'] = source_name
        if source_email:
            source['email'] = source_email

        if limit is not None:
            assert(type(limit) == int)

        data = {
            'user_id': str(user_id),
            'filter_suggested_seen': filter_suggested_seen,
            'filter_existing_users': filter_existing_users,
            'filter_invites_sent': filter_invites_sent,
            'promote_existing_users': promote_existing_users,
            'source': source,
            'entries': entries,
            'limit': limit
        }

        data = json.dumps(data)

        return self._request('POST', '/address-book', data)

    def post_invites_accepted(self, **kwargs):
        """
        Wrapped method for POST of /invites-accepted endpoint

        Documentation - https://docs.yesgraph.com/docs/invites-accepted
        """

        entries = kwargs.get('entries', None)

        if entries and type(entries) == list:
            data = {'entries': entries}
        else:
            raise ValueError('An entry list is required')

        data = json.dumps(data)

        return self._request('POST', '/invites-accepted', data)

    def post_invites_sent(self, **kwargs):
        """
        Wrapped method for POST of /invites-sent endpoint

        Documentation - https://docs.yesgraph.com/docs/invites-sent
        """

        entries = kwargs.get('entries', None)

        if entries:
            data = {'entries': entries}
        else:
            raise ValueError('An entry list is required')

        data = json.dumps(data)

        return self._request('POST', '/invites-sent', data=data)

    def post_suggested_seen(self, **kwargs):
        """
        Wrapped method for POST of /invites-accepted endpoint

        Documentation - https://docs.yesgraph.com/docs/suggested-seen
        """

        entries = kwargs.get('entries', None)

        if entries:
            data = {'entries': entries}
        else:
            raise ValueError('An entry list is required')

        data = json.dumps(data)

        return self._request('POST', '/suggested-seen', data=data)

    def post_users(self, users):
        """
        Wrapped method for POST of users endpoint

        Documentation - https://docs.yesgraph.com/docs/users
        """

        data = json.dumps(users)

        return self._request('POST', '/users', data=data)

    def get_followers(self, type_name, identifier):
        """
        Wrapped method for GET of /followers/<type>/<identifier>/

        Documentation - https://docs.yesgraph.com/v0/docs/followerstypeidentifier
        """
        if type_name not in ['user_id', 'email', 'phone']:
            raise ValueError("type_name must be 'user_id', 'email', or 'phone'")
        if not identifier:
            raise ValueError("Must have a non-null identifier")

        endpoint = '/followers/{0}/{1}'.format(type_name, identifier)

        return self._request('GET', endpoint)
