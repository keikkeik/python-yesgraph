import json

import requests


# TODOs
# -- add documentation links and a bit of info for each endpoint
# -- figure out a way to encapsulate the parameters representing an addressbook source
# -- complete implementation of invite sent/accepted and users post/get


class YesGraphAPI(object):

    def __init__(self, secret_key, url='https://api.yesgraph.com/v0/'):
        self.secret_key = secret_key
        self.base_url = url

        s = requests.Session()
        s.headers.update({
            'Authorization': 'Bearer {}'.format(self.secret_key),
            'Content-Type': 'application/json',
        })
        self.session = s

    def build_url(self, base, path):
        return '{}/{}'.format(base.rstrip('/'), path.lstrip('/'))

    def request(self, verb, endpoint, data=None):
        """
        Generic request wrapper method that sends an HTTP request.

        Example:
        api = YesGraphAPI('<secret_key_here>')
        api.request('get', '/test')
        """
        if isinstance(data, dict):
            data = json.dumps(data)

        url = self.build_url(self.base_url, endpoint)
        resp = getattr(self.session, verb)(url, data=data)
        if not resp.ok:
            resp.raise_for_status()

        return resp.json()

    # ENDPOINTS
    def get_address_book(self, user_id):
        """
        Wrapped method for GET of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/#get-address-bookuser_id
        """
        return self.request('get', '/address-book/{}'.format(str(user_id)))

    def post_address_book(self, user_id, entries, source_name=None,
                          source_email=None, source_type=None):
        """
        Wrapped method for POST of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/#post-address-book
        """
        source = {}
        if source_name:
            source['name'] = source_name

        if source_email:
            source['email'] = source_email

        source['type'] = source_type if source_type else 'gmail'

        payload = json.dumps({
            'user_id': str(user_id),
            'source': source,
            'entries': entries,
        })
        return self.request('post', '/address-book', payload)

    def get_client_key(self, user_id):
        """
        Wrapped method for POST of /client-key endpoint

        Documentation - https://www.yesgraph.com/docs/#obtaining-a-client-api-key
        """
        payload = json.dumps({'user_id': str(user_id)})
        return self.request('post', '/client-key', payload)

    def get_contacts(self, user_id):
        """
        Wrapped method for GET of /contacts endpoint

        Documentation - https://www.yesgraph.com/docs/#get-contactsuser_id
        """
        return self.request('get', '/contacts/{}'.format(str(user_id)))

    def post_invite_accepted(self, new_user_id, invitee_id, invitee_type,
                             accepted_at=None):
        """
        Wrapped method for POST of /invite-accepted endpoint

        Documentation - https://www.yesgraph.com/docs/#post-invite-accepted
        """
        data = {
            'new_user_id': str(new_user_id),
            'invitee_id': str(invitee_id),
            'invitee_type': invitee_type,
        }
        if accepted_at:
            data['accepted_at'] = accepted_at

        payload = json.dumps(data)

        return self.request('post', '/invite-accepted', payload)

    def post_invite_sent(self, user_id, invitee_id, invitee_type, sent_at):
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
            data['sent_at'] = sent_at

        payload = json.dumps(data)

        return self.request('post', '/invite-sent', payload)

    def test(self):
        """
        Wrapped method for GET of /test endpoint

        Documentation - https://www.yesgraph.com/docs/#get-test
        """
        return self.request('get', '/test')

    def get_users(self):
        """
        Wrapped method for GET of /users endpoint

        Documentation - https://www.yesgraph.com/docs/#get-users
        """
        return self.request('get', '/users')

    def post_users(self, entries):
        """
        Wrapped method for POST of users endpoint

        Documentation - https://www.yesgraph.com/docs/#post-users
        """
        payload = json.dumps(entries)
        return self.request('post', '/users', payload)
