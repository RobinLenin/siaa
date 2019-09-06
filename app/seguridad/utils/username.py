from threading import current_thread
from django.middleware.common import CommonMiddleware
_requests = {}


def get_username():
    t = current_thread()
    if t not in _requests:
        return None
    return _requests[t]


class RequestMiddleware(CommonMiddleware):
    def process_request(self, request):
        _requests[current_thread()] = request
