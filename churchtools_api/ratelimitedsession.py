"""This code is used to wrap the most common requests into a rate limited model.

ChurchTools API usually responds code 429 on excessive use
 - repeating request after timeout will suceed
"""
import logging
from time import sleep
from typing import override

import requests

logger = logging.getLogger(__name__)


class RateLimitedSession(requests.Session):
    """This class wraps request.Sessions most important methods.

    with rate limits and retry
    """

    def __init__(self) -> None:
        """Inits session with additional params."""
        logger.debug("init rate limited session")
        super().__init__()

    def _rate_limited_request(self, method, url, **kwargs) -> requests.Response:  # noqa: ANN001, ANN003
        """Rate limiting execution of original request method."""
        result = super().request(method, url, **kwargs)

        while result.status_code == requests.codes.too_many_requests:
            logger.info("rate limit reached - waiting 15 sec before repeating request")
            sleep(15.0)
            result = self._rate_limited_request(method=method, url=url, **kwargs)

        return result

    @override
    def request(self, method, url, **kwargs) -> requests.Response:  # noqa: ANN001, ANN003
        """See sessions.requests for more details.

        Only adds rate_limit
        """
        return self._rate_limited_request(method, url, **kwargs)
