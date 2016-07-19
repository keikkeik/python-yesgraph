import platform
import warnings
from collections import Iterable
from datetime import datetime
import json

import six
from requests import Request, Session

from six.moves.urllib.parse import quote_plus

__version__ = '0.6.3'


def deprecation(message):
    warnings.warn(message, DeprecationWarning, stacklevel=2)


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
        data = json.dumps({'user_id': str(user_id)})
        return self._request('POST', '/client-key', data)

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

    def backfill_address_book(self, user_id, entries, source_type, source_name=None,
                              source_email=None):
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

        data = {
            'user_id': str(user_id),
            'source': source,
            'entries': entries,
        }

        data = json.dumps(data)

        return self._request('POST', '/backfill/address-book', data)

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

    def post_invite_accepted(self, **kwargs):
        """
        Wrapped method for POST of /invite-accepted endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-invite-accepted
        """
        email = kwargs.get('email')
        phone = kwargs.get('phone')
        accepted_at = kwargs.get('accepted_at')
        new_user_id = kwargs.get('new_user_id')
        deprecation(""" POST /invite-accepted (single) has been deprecated in
                        favor of the batch endpoint POST /invites-accepted """)

        if 'invitee_id' in kwargs or 'invitee_type' in kwargs:
            deprecation('invitee_id and invitee_type fields have been deprecated. '
                        'Please use the `email` or `phone` fields instead.')

            invitee_id = kwargs['invitee_id']
            invitee_type = kwargs.get('invitee_type', 'email')
            if invitee_type == 'email' and not email:
                email = str(invitee_id)
            elif invitee_type in ('sms', 'phone') and not phone:
                phone = str(invitee_id)
            else:
                raise ValueError('Unknown invitee_type: {}'.format(invitee_type))

        if not (email or phone):
            raise ValueError('An `email` or `phone` key is required')

        data = {}
        if email:
            data['email'] = email
        if phone:
            data['phone'] = phone
        if accepted_at:
            data['accepted_at'] = format_date(accepted_at)
        if new_user_id:
            data['new_user_id'] = str(new_user_id)

        entries = {'entries': [data]}

        return self.post_invites_accepted(**entries)

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

    def post_invite_sent(self, user_id, **kwargs):
        """
        Wrapped method for POST of /invite-sent endpoint

        Documentation - https://www.yesgraph.com/docs/reference#post-invite-sent
        """
        email = kwargs.get('email')
        phone = kwargs.get('phone')
        sent_at = kwargs.get('sent_at')
        deprecation(""" POST /invite-sent (single) has been deprecated in
                        favor of the batch endpoint POST /invites-sent """)

        if 'invitee_id' in kwargs or 'invitee_type' in kwargs:
            deprecation('invitee_id and invitee_type fields have been deprecated. '
                        'Please use the `email` or `phone` fields instead.')

            invitee_id = kwargs['invitee_id']
            invitee_type = kwargs.get('invitee_type', 'email')
            if invitee_type == 'email' and not email:
                email = str(invitee_id)
            elif invitee_type in ('sms', 'phone') and not phone:
                phone = str(invitee_id)
            else:
                raise ValueError('Unknown invitee_type: {}'.format(invitee_type))

        if not (email or phone):
            raise ValueError('An `email` or `phone` key is required')

        data = {
            'user_id': str(user_id),
        }

        if email:
            data['email'] = email
        if phone:
            data['phone'] = phone
        if sent_at:
            data['sent_at'] = format_date(sent_at)

        entries = {'entries': [data]}

        return self.post_invites_sent(**entries)

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
