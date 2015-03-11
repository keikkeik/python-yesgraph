import pytest
from yesgraph import YesGraphAPI

from .data import entries, users

TEST_KEY = 'test-WzEsMSwiVGVzdFllc0dyYXBoIl0.B7QyrQ.0T5kC7lIdQ1zrOzx-Ra746zusKQ'


@pytest.fixture
def api():
    return YesGraphAPI(TEST_KEY, url='http://localhost:5001/v0/')


def test_test_endpoint(api):
    assert api.test()


def test_get_address_book(api):
    assert api.get_address_book(1)


def test_post_address_book(api):
    assert api.post_address_book(1, entries, 'Jonathan Chu', 'jonathan@yesgraph.com', 'gmail')


def test_get_client_key(api):
    assert api.get_client_key(1)


def test_get_contacts(api):
    assert api.get_contacts(1)


def test_post_invite_accepted(api):
    assert api.post_invite_accepted(42, 'john.smith@gmail.com', 'email', '2015-03-03T20:16:12+00:00')


def test_post_invite_sent(api):
    assert api.post_invite_sent(42, 'john.smith@gmail.com', 'email', '2015-02-28T20:16:12+00:00')


def test_get_users(api):
    assert api.get_users()


def test_post_users(api):
    assert api.post_users(users)
