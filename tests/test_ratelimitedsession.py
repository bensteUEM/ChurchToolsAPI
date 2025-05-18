"""This test module is used to verify integrity of the Ratelimited session."""

import json
import logging
import logging.config
from pathlib import Path

import pytest

from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestsRateLimitedSession(TestsChurchToolsApiAbstract):
    """Test for Rate limits."""

    def test_no_rate_limit(self, caplog: pytest.LogCaptureFixture) -> None:
        """Reference time for 250 requests without throttle using google.com."""
        SAMPLE_SONG_ID = 408

        with caplog.at_level(logging.INFO, logger="ratelimitedsession"):
            for _i in range(750):
                self.api.get_songs(song_id=SAMPLE_SONG_ID)
        EXPECTED_MESSAGES = [
            "rate limit reached - waiting 15 sec before repeating request"
        ]

        assert caplog.messages == EXPECTED_MESSAGES
