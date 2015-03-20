import json

from requests import Response
from requests.packages.urllib3.response import HTTPResponse
from requests.structures import CaseInsensitiveDict


def make_fake_response(status, doc):
    """
    Helper function to conveniently build a fake Response instance from
    a status code and a dictionary, as if this is a response coming from the
    YesGraph API.
    """
    text = json.dumps(doc)
    body = text.encode('utf-8')  # body must be bytes

    # First, we need to build a urllib3 response...
    raw_response = HTTPResponse(body)

    # ...and let requests' Response wrap it
    response = Response()
    response.status_code = status
    response.headers = CaseInsensitiveDict({
        'Content-Type': 'application/json',
    })
    response.raw = raw_response
    return response
