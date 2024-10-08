import ast
import json
import logging
import logging.config
import os
from abc import ABC
from pathlib import Path

from churchtools_api.churchtools_api import ChurchToolsApi

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestsChurchToolsApiAbstract(ABC):  # noqa: B024
    """This is supposed to be the base configuration for PyTest test classes that require API access."""

    def setup_class(self) -> None:
        if "CT_TOKEN" in os.environ:
            self.ct_token = os.environ["CT_TOKEN"]
            self.ct_domain = os.environ["CT_DOMAIN"]
            users_string = os.environ["CT_USERS"]
            self.ct_users = ast.literal_eval(users_string)
            logger.info("using connection details provided with ENV variables")
        else:
            from secure.config import ct_token

            self.ct_token = ct_token
            from secure.config import ct_domain

            self.ct_domain = ct_domain
            from secure.config import ct_users

            self.ct_users = ct_users
            logger.info("using connection details provided from secrets folder")

        self.api = ChurchToolsApi(domain=self.ct_domain, ct_token=self.ct_token)

        logger.info("Executing Tests RUN")
