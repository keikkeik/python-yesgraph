import json

import requests
from cached_property import cached_property


# TODOs
# -- add documentation links and a bit of info for each endpoint
# -- abstract base API url from endpoint names
# -- figure out a way to encapsulate the parameters representing an addressbook source
# -- parse JSON returns when logical and useful, like returning the client key
# -- complete implementation of invite sent/accepted and users post/get


class YesGraphAPI(object):

    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.headers = {
            'Authorization': 'Bearer {}'.format(self.secret_key),
            'Content-Type': 'application/json',
        }
        self.base_url = 'http://localhost:5001/v0'

    @cached_property
    def session(self):
        session = requests.Session()
        session.headers.update({
            'Authorization': 'Bearer {}'.format(self.secret_key),
            'Content-Type': 'application/json',
        })
        return session

    def get(self, endpoint, data=None):
        """
        Generic `get` wrapper method that sends a GET request.

        Example:
        api = YesGraphAPI('<secret_key_here>')
        api.get('/test')
        """
        resp = self.session.get(self.base_url + endpoint, data=data)
        if not resp.ok:
            resp.raise_for_status()
        else:
            data = resp.json()
            return data

    def post(self, endpoint, data=None):
        """
        Generic `post` wrapper method that sends a POST request.

        Example:
        api = YesGraphAPI('<secret_key_here>')
        api.get('/address-book', entries)
        """
        if isinstance(data, dict):
            data = json.dumps(data)

        resp = self.session.post(self.base_url + endpoint, data=data)
        if not resp.ok:
            resp.raise_for_status()
        else:
            data = resp.json()
            return data

    # ENDPOINTS
    def get_address_book(self, user_id):
        """
        Wrapped method for GET of /address-book endpoint

        Documentation - https://www.yesgraph.com/docs/#get-address-bookuser_id
        """
        return self.get('/address-book/' + str(user_id))

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
        return self.post('/address-book', payload)

    def generate_client_key(self, user_id):
        """
        Wrapped method for POST of /client-key endpoint

        Documentation - https://www.yesgraph.com/docs/#obtaining-a-client-api-key
        """
        payload = json.dumps({'user_id': str(user_id)})
        return self.post('/client-key', payload)

    def get_contacts(self, user_id):
        """
        Wrapped method for GET of /contacts endpoint

        Documentation - https://www.yesgraph.com/docs/#get-contactsuser_id
        """
        return self.get('/contacts/' + str(user_id))

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

        return self.post('/invite-accepted', payload)

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

        return self.post('/invite-sent', payload)

    def test(self):
        """
        Wrapped method for GET of /test endpoint

        Documentation - https://www.yesgraph.com/docs/#get-test
        """
        return self.get('/test')

    def users_get(self):
        raise NotImplementedError

    def users_post(self):
        raise NotImplementedError
