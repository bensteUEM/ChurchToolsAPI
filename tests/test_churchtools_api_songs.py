"""module test song."""

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


class TestChurchtoolsApiSongs(TestsChurchToolsApiAbstract):
    """Test for Songs."""

    def test_get_songs(self) -> None:
        """Check get songs.

        1. Test requests all songs and checks that result has more than 50 elements
         (hence default pagination works)
        2. Test requests song 2034 and checks that result matches "sample".

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_SONG = {"id": 2034, "name": "sample"}

        songs = self.api.get_songs()
        LENGTH_OF_DEFAULT_PAGINATION = 50
        assert len(songs) > LENGTH_OF_DEFAULT_PAGINATION

        song = self.api.get_songs(song_id=SAMPLE_SONG["id"])[0]
        assert song["id"] == SAMPLE_SONG["id"]
        assert song["name"] == SAMPLE_SONG["name"]

    def test_get_song_category_map(self) -> None:
        """Checks that a dict with respective known values.

        is returned when requesting song categories
        IMPORTANT - This test method and the parameters used
            depend on the target system!
        Requires the connected test system to have a category "Test"
        mapped as ID 13 (or changed if other system)
        :return:
        """
        EXPECTED_CATEGORY = {"Test": 13}

        song_catgegory_dict = self.api.get_song_category_map()
        assert all(
            item in song_catgegory_dict.items() for item in EXPECTED_CATEGORY.items()
        )

    def test_lookup_song_category_as_id(self, caplog: pytest.LogCaptureFixture) -> None:
        """Checks lookup of song category by text.

        On ELKW1610.KRZ.TOOLS "Feiert Jesus 5" = id8
        """
        result = self.api.get_song_source_map()

        # known sample
        SAMPLE_CATEGORY_NAME = "Feiert Jesus 5"
        EXPECTED_ID = 8

        result = self.api.lookup_song_category_as_id(category_name=SAMPLE_CATEGORY_NAME)
        assert result == EXPECTED_ID

        # invalid sample
        SAMPLE_CATEGORY_NAME = "Does not exist"
        EXPECTED_ID = None

        caplog.clear()
        with caplog.at_level(logging.WARNING, logger="churchtools_api.songs"):
            result = self.api.lookup_song_category_as_id(
                category_name=SAMPLE_CATEGORY_NAME
            )
        assert result == EXPECTED_ID
        EXPECTED_MESSAGES = [
            "Can not find song category (Does not exist) on this system"
        ]
        assert caplog.messages == EXPECTED_MESSAGES

    def test_create_edit_delete_song(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test method used to create a new song.

        edit it's metadata and remove the song.

        Does only test metadata not attachments or arrangements
        IMPORTANT - This test method and the parameters used
            depend on the target system!
        On ELKW1610.KRZ.TOOLS songcategory_id 13 is TEST

        Returns: None
        """
        title = "Test_bezeichnung1"
        songcategory_id = 13

        # 1. Create Song after and check it exists with all params
        song_id = self.api.create_song(name=title, songcategory_id=songcategory_id)
        assert song_id is not None

        ct_song = self.api.get_songs(song_id=song_id)[0]
        assert ct_song["name"] == title
        assert ct_song["author"] is None
        assert ct_song["category"]["id"] == songcategory_id

        # 2. Edit Song title and check it exists with all params
        self.api.edit_song(song_id, name="Test_bezeichnung2")
        ct_song = self.api.get_songs(song_id=song_id)[0]
        assert ct_song["author"] is None
        assert ct_song["name"] == "Test_bezeichnung2"

        # 3. Edit all fields and check it exists with all params
        data = {
            "name": "Test_bezeichnung3",
            "songcategory_id": 1,
            "author": "Test_author",
            "copyright": "Test_copyright",
            "ccli": "Test_ccli",
            "should_practice": 1,
        }
        self.api.edit_song(
            song_id=song_id,
            songcategory_id=data["songcategory_id"],
            name=data["name"],
            author=data["author"],
            copyright=data["copyright"],
            ccli=data["ccli"],
            should_practice=data["should_practice"],
        )
        ct_song = self.api.get_songs(song_id=song_id)[0]
        assert ct_song["name"] == data["name"]
        assert ct_song["category"]["id"] == data["songcategory_id"]
        assert ct_song["author"] == data["author"]
        assert ct_song["copyright"] == data["copyright"]
        assert ct_song["ccli"] == data["ccli"]
        assert ct_song["shouldPractice"] == data["should_practice"]

        # Delete Song
        self.api.delete_song(song_id)

        caplog.clear()
        with caplog.at_level(logging.INFO, logger="churchtools_api_songs"):
            ct_song = self.api.get_songs(song_id=song_id)
        EXPECTED_MESSAGES = [
            f"Did not find song ({song_id}) with CODE 404",
        ]
        assert caplog.messages == EXPECTED_MESSAGES
        assert ct_song is None

    def test_add_remove_song_tag(self) -> None:
        """Test method used to add and remove the test tag to some song.

        Tag ID and Song ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS song_id 408 (sample_no_ct_attachement)
            and tag_id 163 (Test)

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        song ID 408 is tagged with 163 "Test"

        Returns: None
        """
        SAMPLE_SONG_ID = 408
        TEST_SONG_TAG = "Test"

        tag_is_assigned = self.api.contains_song_tag(
            song_id=SAMPLE_SONG_ID, song_tag_name=TEST_SONG_TAG
        )
        assert tag_is_assigned

        remove_success = self.api.remove_tag(
            domain_type="song", domain_id=SAMPLE_SONG_ID, tag_name=TEST_SONG_TAG
        )
        assert remove_success

        tag_is_assigned = self.api.contains_song_tag(
            song_id=SAMPLE_SONG_ID, song_tag_name=TEST_SONG_TAG
        )
        assert not tag_is_assigned

        add_success = self.api.add_tag(
            domain_type="song", domain_id=SAMPLE_SONG_ID, tag_name=TEST_SONG_TAG
        )
        assert add_success

        tag_is_assigned = self.api.contains_song_tag(
            song_id=SAMPLE_SONG_ID, song_tag_name=TEST_SONG_TAG
        )
        assert tag_is_assigned

    def test_get_songs_with_tag(self) -> None:
        """Test method to check if fetching all songs with a specific tag works.

        songId and tag_id will vary depending on the server used

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        song ID 408 is tagged with 163 "Test"
        """
        SAMPLE_TAG_NAME = "Test"
        SAMPLE_SONG_ID = 408

        result = self.api.get_songs_by_tag(song_tag_name=SAMPLE_TAG_NAME)
        result_ids = [song["id"] for song in result]
        assert SAMPLE_SONG_ID in result_ids

    def test_get_song_source_map(self) -> None:
        """Checks respective method returns some data.

        On ELKW1610.KRZ.TOOLS there are at least two song sources configures
        """
        result = self.api.get_song_source_map()
        assert len(result) > 1
        assert all(isinstance(item, dict) for item in result.values())

    def test_lookup_song_source_as_id(self, caplog: pytest.LogCaptureFixture) -> None:
        """Checks respective method returns some data.

        On ELKW1610.KRZ.TOOLS "T" = "Test" = id12
        """
        result = self.api.get_song_source_map()
        SAMPLE_SHORTNAME = "T"
        SAMPLE_LONGNAME = "Test"
        EXPECTED_ID = 12

        # shortname
        result = self.api.lookup_song_source_as_id(shortname=SAMPLE_SHORTNAME)
        assert result == EXPECTED_ID

        # longname
        result = self.api.lookup_song_source_as_id(longname=SAMPLE_LONGNAME)
        assert result == EXPECTED_ID

        # too many args
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger="churchtools_api.songs"):
            result = self.api.lookup_song_source_as_id(
                longname=SAMPLE_LONGNAME, shortname=SAMPLE_SHORTNAME
            )
        assert result is None
        EXPECTED_MESSAGES = ["too many arguments - either use shortname or longname"]
        assert caplog.messages == EXPECTED_MESSAGES

        # no arguments
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger="churchtools_api.songs"):
            result = self.api.lookup_song_source_as_id()
        assert result is None
        EXPECTED_MESSAGES = [
            "missing argument longname or shortname required",
        ]
        assert caplog.messages == EXPECTED_MESSAGES

    def test_get_song_arrangement(self) -> None:
        """Checking song arrangement retrieval."""
        SAMPLE_SONG_ID = 408

        # part 1 default arrangement
        result = self.api.get_song_arrangement(song_id=SAMPLE_SONG_ID)
        assert isinstance(result, dict)
        EXPECTED_KEYS = [
            "id",
            "name",
            "isDefault",
            "sourceName",
            "sourceReference",
            "keyOfArrangement",
            "bpm",
            "beat",
            "duration",
            "note",
            "links",
            "files",
            "meta",
        ]
        assert all(key in result for key in EXPECTED_KEYS)

        SAMPLE_SONG_ARRANGEMENT_ID = result["id"]

        # part 2 check specific arrangement id
        result = self.api.get_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=SAMPLE_SONG_ARRANGEMENT_ID
        )
        assert isinstance(result, dict)
        EXPECTED_KEYS = [
            "id",
            "name",
            "isDefault",
            "sourceName",
            "sourceReference",
            "keyOfArrangement",
            "bpm",
            "beat",
            "duration",
            "note",
            "links",
            "files",
            "meta",
        ]
        assert all(key in result for key in EXPECTED_KEYS)

    def test_create_edit_delete_song_arrangement(self) -> None:
        """Check create edit and delete methods for song arrangements."""
        SAMPLE_SONG_ID = 408

        # create
        SAMPLE_ARRANGEMENT_NAME = "test_create_song_arrangement"
        arrangement_id = self.api.create_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_name=SAMPLE_ARRANGEMENT_NAME
        )
        assert isinstance(arrangement_id, int)
        created_arrangement = self.api.get_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id
        )
        assert created_arrangement["name"] == SAMPLE_ARRANGEMENT_NAME

        SAMPLE_SOURCE = {"12": "T"}

        # edit source as text and changed params
        SAMPLE_ARRANGEMENT_NAME2 = "TEST_BEZEICHNUNG"
        SAMPLE_PARAMS = {
            "name": SAMPLE_ARRANGEMENT_NAME2,
            "sourceName": next(iter(SAMPLE_SOURCE.values())),
            "sourceReference": "source_ref",
            "key": "F",
            "tempo": 50,
            "beat": "beat",
            "duration": 60,
            "description": "note",
        }
        key_map = {
            "sourceReference": "source_reference",
            "sourceName": "source_name_short",
        }
        formatted_params = {key_map.get(k, k): v for k, v in SAMPLE_PARAMS.items()}

        was_applied = self.api.edit_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id, **formatted_params
        )

        assert was_applied
        created_arrangement = self.api.get_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id
        )
        assert created_arrangement["name"] == SAMPLE_ARRANGEMENT_NAME2
        assert all(
            created_arrangement[expected_key] == expected_value
            for expected_key, expected_value in SAMPLE_PARAMS.items()
        )

        # delete
        was_deleted = self.api.delete_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id
        )
        assert was_deleted
