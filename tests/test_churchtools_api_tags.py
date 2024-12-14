"""module test tags."""

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


class TestChurchtoolsApiResources(TestsChurchToolsApiAbstract):
    """Test for Tags."""

    @pytest.mark.skip(
        "See Github issue 92 - and CT Support Case 136613 "
        "- at present no delete available"
    )
    def test_create_get_delete_tags(self) -> None:
        """Checks creation and deletition of events using get events."""
        SAMPLE_TAG_NAME = "testing_new_tag"
        SAMPLE_TYPE = "persons"

        existing_tags = self.api.get_tags(tag_type=SAMPLE_TYPE)
        assert SAMPLE_TAG_NAME not in [tag["name"] for tag in existing_tags]

        self.api.create_tag(name=SAMPLE_TAG_NAME, tag_type=SAMPLE_TYPE)

        existing_tags = self.api.get_tags(tag_type=SAMPLE_TYPE)
        assert SAMPLE_TAG_NAME not in [tag["name"] for tag in existing_tags]

        self.api.delete_tag(tag_type=SAMPLE_TYPE, name=SAMPLE_TAG_NAME)
        existing_tags = self.api.get_tags(tag_type=SAMPLE_TYPE)
        assert SAMPLE_TAG_NAME not in [tag["name"] for tag in existing_tags]

    def test_get_tags(self) -> None:
        """Test function for get_tags() with default type song.

        On ELKW1610.KRZ.TOOLS tag ID 49 has the name To Do
        """
        SAMPLE_TAG = {49: "ToDo"}

        result = self.api.get_tags(type="songs")
        assert len(result) > 0
        test_tag = next(item for item in result if item["id"] == next(iter(SAMPLE_TAG)))
        assert test_tag["id"] == next(iter(SAMPLE_TAG))
        assert test_tag["name"] == next(iter(SAMPLE_TAG.values()))
