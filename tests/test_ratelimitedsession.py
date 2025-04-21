"""This test module is used to verify integrity of the Ratelimited session."""
#TODO@bensteUEM: inquiry to CT Team 147987 for configured threshold
# https://github.com/bensteUEM/ChurchToolsAPI/issues/37

import json
import logging
import logging.config
import time
from pathlib import Path

import pytest
import requests

from churchtools_api.ratelimitedsession import RateLimitedSession

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)

# Make sure test values are adjusted
#  - e.g. 250* google.com with 10 req per 2seconds ~= 50 sec
#  - e.g. 250* google.com with no threshold ~= 30 sec
SAMPLE_URL = "https://google.com"
EXPECTED_TIME = 30


@pytest.mark.skip("execute only if ratelimit is decreased")
def test_no_rate_limit() -> None:
    """Reference time for 250 requests without throttle using google.com.

    Actual time might depend on internet speed!

    Only checks GET request for simplification.
    """
    session = requests.Session()

    start = time.perf_counter()
    for _i in range(250):
        session.get(url=SAMPLE_URL)
    end = time.perf_counter()

    assert end - start < EXPECTED_TIME

@pytest.mark.skip("execute only if ratelimit is decreased")
def test_rate_limited() -> None:
    """Reference time for 250 requests with throttle using google.com.

    Only checks GET request for simplification.
    """
    session = RateLimitedSession()

    start = time.perf_counter()
    for _i in range(250):
        session.get(url=SAMPLE_URL)
    end = time.perf_counter()

    assert end-start > EXPECTED_TIME
