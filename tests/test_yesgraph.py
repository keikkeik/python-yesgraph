import pytest
from yesgraph import YesGraphAPI

TEST_KEY = 'test-WzEsMSwiVGVzdFllc0dyYXBoIl0.B7QyrQ.0T5kC7lIdQ1zrOzx-Ra746zusKQ'


@pytest.fixture
def api():
    return YesGraphAPI(TEST_KEY)


def test_test_endpoint(api):
    assert api.test()
