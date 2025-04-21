"""This code is used to wrap the most common requests into a rate limited model.

ChurchTools API usually accepts X / sec requests and will return an error if exceeded
"""
#TODO@bensteUEM: inquiry to CT Team 147987 for configured thresholds
# https://github.com/bensteUEM/ChurchToolsAPI/issues/37

from typing import override

import requests
from ratelimit import limits, sleep_and_retry


class RateLimitedSession(requests.Session):
    """This class wraps request.Sessions most important methods.

    with rate limits and retry
    """

    MAX_CALLS = 50
    LIMIT_PERIOD_SECONDS = 2

    def __init__(self) -> None:
        """Inits session with additional params."""
        super().__init__()

    @sleep_and_retry
    @limits(calls=MAX_CALLS, period=LIMIT_PERIOD_SECONDS)
    def _rate_limited_request(self, method, url, **kwargs) -> requests.Response:  # noqa: ANN001, ANN003
        """Rate limiting execution of original request method."""
        return super().request(method, url, **kwargs)

    @override
    def request(self, method, url, **kwargs) -> requests.Response:  # noqa: ANN001, ANN003
        """See sessions.requests for more details.

        Only adds rate_limit
        """
        return self._rate_limited_request(method, url, **kwargs)
