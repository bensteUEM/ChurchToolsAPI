"""module test persons."""

import json
import logging
import logging.config
from pathlib import Path

from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestChurchtoolsApiTags(TestsChurchToolsApiAbstract):
    """Test for Tags."""

    def test_get_tags(self) -> None:
        """Test function for get_tags() with default type song.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.

        On ELKW1610.KRZ.TOOLS tag ID 49 has the name "ToDo"

        Returns:
            None
        """
        result = self.api.get_tags(domain_type="song")

        EXPECTED_MIN_RESULT = {"Test": 163}
        assert any(item["name"] in EXPECTED_MIN_RESULT for item in result)
        assert any(item["id"] in EXPECTED_MIN_RESULT.values() for item in result)

    def test_get_tags_id_dict(self) -> None:
        """Test function for get_tags() with default type song.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.

        On ELKW1610.KRZ.TOOLS tag ID 49 has the name "ToDo"

        Returns:
            None
        """
        result = self.api.get_tags(domain_type="song", rtype="id_dict")
        assert len(result) > 0

        EXPECTED_MIN_RESULT = {163: "Test"}
        assert all(item in result.items() for item in EXPECTED_MIN_RESULT.items())

    def test_get_tags_name_dict(self) -> None:
        """Test function for get_tags() with default type song.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.

        On ELKW1610.KRZ.TOOLS tag ID 49 has the name "ToDo"

        Returns:
            None
        """
        result = self.api.get_tags(domain_type="song", rtype="name_dict")

        EXPECTED_MIN_RESULT = {"Test": 163}
        assert all(item in result.items() for item in EXPECTED_MIN_RESULT.items())

    def test_create_get_delete_tag(self) -> None:
        """Checks create, get and delete methods for tags usings "song" as sample.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.

        On ELKW1610.KRZ.TOOLS song ID 2034 is used for testing
        """
        SAMPLE_SONG_ID = 2034
        SAMPLE_TAG_NAME = "test_create_get_delete_tag"

        is_assigned = any(
            tag["name"] == SAMPLE_TAG_NAME
            for tag in self.api.get_tag(
                domain_type="song",
                domain_id=SAMPLE_SONG_ID,
            )
        )
        assert not is_assigned

        tag_assigned = self.api.add_tag(
            domain_type="song",
            domain_id=SAMPLE_SONG_ID,
            tag_name=SAMPLE_TAG_NAME,
        )
        assert tag_assigned

        is_assigned = any(
            tag["name"] == SAMPLE_TAG_NAME
            for tag in self.api.get_tag(
                domain_type="song",
                domain_id=SAMPLE_SONG_ID,
            )
        )
        assert is_assigned

        is_removed = self.api.remove_tag(
            domain_type="song",
            domain_id=SAMPLE_SONG_ID,
            tag_name=SAMPLE_TAG_NAME,
        )

        assert is_removed

        is_assigned = any(
            tag["name"] == SAMPLE_TAG_NAME
            for tag in self.api.get_tag(
                domain_type="song",
                domain_id=SAMPLE_SONG_ID,
            )
        )
        assert not is_assigned

    def test_get_song_tag_original(self) -> None:
        """Cchek song tag can be retrieved and returned as original.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        song ID 408 is tagged with 163 "Test"
        """
        SAMPLE_SONG_ID = 408
        result = self.api.get_tag(domain_type="song", domain_id=SAMPLE_SONG_ID)
        EXPECTED_TAG = 163
        assert EXPECTED_TAG in [tag["id"] for tag in result]

    def test_get_song_tag_id_dict(self) -> None:
        """Check song tag can be retrieved and returned as id dict.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        song ID 408 is tagged with 163 "Test"
        """
        SAMPLE_SONG_ID = 408
        result = self.api.get_tag(
            domain_type="song", domain_id=SAMPLE_SONG_ID, rtype="id_dict"
        )
        EXPECTED_MIN_RESULT = {163: "Test"}
        assert all(
            item in [tag["name"] for tag in result.values()]
            for item in EXPECTED_MIN_RESULT.values()
        )
        assert all(key in result for key in EXPECTED_MIN_RESULT)

    def test_get_song_tag_name_dict(self) -> None:
        """Check song tag can be retrieved and returned as name dict.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        song ID 408 is tagged with 163 "Test"
        """
        SAMPLE_SONG_ID = 408
        result = self.api.get_tag(
            domain_type="song", domain_id=SAMPLE_SONG_ID, rtype="name_dict"
        )
        EXPECTED_MIN_RESULT = {"Test": 163}
        assert all(
            item in [tag["id"] for tag in result.values()]
            for item in EXPECTED_MIN_RESULT.values()
        )
        assert all(key in result for key in EXPECTED_MIN_RESULT)
