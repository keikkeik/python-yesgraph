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
            resp.rase_for_status()
        else:
            data = resp.json()
            return data

    # ENDPOINTS
    # documentation
    #   https://www.yesgraph.com/docs/#get-address-bookuser_id
    def addressbook_get(self, user_id):
        url = 'https://api.yesgraph.com/v0/address-book/' + str(user_id)
        return self.api_get(url)

    # documenation
    #    https://www.yesgraph.com/docs/#post-address-book
    def addressbook_post(self, user_id, entries, source_name=None,
                         source_email=None, source_type=None):
        url = 'https://api.yesgraph.com/v0/address-book'
        source = {}
        if source_name:
            source['name'] = source_name
        if source_email:
            source['name'] = source_email
        if source_type:
            source['type'] = source_type

        payload = json.dumps({
            'user_id': str(user_id),
            'source': source,
            'entries': entries,
        })

        return self.api_post(url, payload)

    def client_key(self, user_id):
        url = 'https://api.yesgraph.com/v0/client-key'
        payload = json.dumps({'user_id': '1', })
        return self.api_post(url, payload)

    def contacts(self):
        url = 'https://api.yesgraph.com/v0/contacts/1'
        return self.api_get(url)

    def invite_accepted(self):
        raise NotImplementedError

    def invite_sent(self):
        raise NotImplementedError

    def test(self):
        url = 'https://api.yesgraph.com/v0/test'
        return self.api_get(url)

    def users_get(self):
        raise NotImplementedError

    def users_post(self):
        raise NotImplementedError
