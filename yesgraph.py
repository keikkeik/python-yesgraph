import json
from collections import Iterable
from datetime import datetime

from requests import Request, Session

import six


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

    def _build_url(self, endpoint):
        return '/'.join((self.base_url.rstrip('/'), endpoint.lstrip('/')))

    def _prepare_request(self, method, endpoint, data=None):
        """Builds and prepares the complete request, but does not send it."""
        headers = {
            'Authorization': 'Bearer {0}'.format(self.secret_key),
            'Content-Type': 'application/json',
        }

        url = self._build_url(endpoint)

        # Prepare the data
        if data is not None:
            if is_nonstring_iterable(data):
                data = json.dumps(data)
            else:
                raise TypeError('Argument "data" must be (non-string) iterable, got: {0!r}'.format(data))  # pragma: no cover  # noqa

        req = Request(method, url, data=data, headers=headers)
        prepped_req = self.session.prepare_request(req)
        return prepped_req

    def _request(self, method, endpoint, data=None):  # pragma: no cover
        """
        Builds, prepares, and sends the complete request to the YesGraph API,
        returning the decoded response.
        """
        prepped_req = self._prepare_request(method, endpoint, data=data)
        resp = self.session.send(prepped_req)
        return self._handle_response(resp)

    def _handle_response(self, response):
        """Decodes the HTTP response when successful, or throws an error."""
        response.raise_for_status()
        return response.json()

    def test(self):
        """
        Wrapped method for GET of /test endpoint

        Documentation - https://www.yesgraph.com/docs/#get-test
        """
        return self._request('GET', '/test')

    def get_client_key(self, user_id):
        """
        Wrapped method for POST of /client-key endpoint

        Documentation - https://www.yesgraph.com/docs/#obtaining-a-client-api-key
        """
        return self._request('POST', '/client-key', {'user_id': str(user_id)})['client_api_key']

    def get_address_book(self, user_id):
        """
        Wrapped method for GET of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/#get-address-bookuser_id
        """
        return self._request('GET', '/address-book/{0}'.format(str(user_id)))

    def post_address_book(self, user_id, entries,
                          source_type, source_name=None, source_email=None):
        """
        Wrapped method for POST of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/#post-address-book
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

        Documentation - https://www.yesgraph.com/docs/#post-invite-accepted
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

        Documentation - https://www.yesgraph.com/docs/#post-invite-sent
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

        Documentation - https://www.yesgraph.com/docs/#get-users
        """
        return self._request('GET', '/users')

    def post_users(self, users):
        """
        Wrapped method for POST of users endpoint

        Documentation - https://www.yesgraph.com/docs/#post-users
        """
        return self._request('POST', '/users', users)
