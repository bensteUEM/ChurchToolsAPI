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

    @pytest.mark.skip(
        "This test requires a high rate of request in a short time "
        "and is only enabled if checked on purpose. "
        "It is skipped to avoid unnecesary system load"
    )
    def test_rate_limit_logged(self, caplog: pytest.LogCaptureFixture) -> None:
        """This test tries to send many request in order to log a "rate limit message.

        it will only work if your client sends these requests fast enough.

        Args:
            caplog: _description_
        """
        with caplog.at_level(logging.INFO, logger="ratelimitedsession"):
            for _i in range(1000):
                self.api.get_calendars()
        EXPECTED_MESSAGES = [
            "rate limit reached - waiting 15 sec before repeating request"
        ]

        assert all(message in EXPECTED_MESSAGES for message in caplog.messages)
