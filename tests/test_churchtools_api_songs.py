"""module test song."""

import json
import logging
import logging.config
from pathlib import Path

import requests

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
        """1. Test requests all songs and checks that result has more than 50 elements
         (hence default pagination works)
        2. Test requests song 2034 and checks that result matches "sample".

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_SONG_ID = 2034

        songs = self.api.get_songs()
        LENGTH_OF_DEFAULT_PAGINATION = 50
        assert len(songs) > LENGTH_OF_DEFAULT_PAGINATION

        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        assert song["id"] == SAMPLE_SONG_ID
        assert song["name"] == "sample"

    def test_get_song_ajax(self) -> None:
        """Testing legacy AJAX API to request one specific song.

        1. Test requests song 408 and checks that result matches Test song
        Keys were last updated / checked with ChurchTools v3.115.1

        IMPORTANT - This test method and the parameters used
            depend on the target system!

        """
        SAMPLE_SONG_ID = 2034
        song = self.api.get_song_ajax(song_id=SAMPLE_SONG_ID)
        assert isinstance(song, dict)

        EXPECTED_KEYS = [
            "id",
            "bezeichnung",
            "songcategory_id",
            "practice_yn",
            "author",
            "ccli",
            "copyright",
            "note",
            "created_date",
            "created_pid",
            "modified_date",
            "modified_pid",
            "arrangement",
            "tags",
        ]

        assert all(key in EXPECTED_KEYS for key in song)

        assert int(song["id"]) == SAMPLE_SONG_ID
        assert song["bezeichnung"] == "sample"

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

    def test_lookup_song_category_as_id(self, caplog) -> None:
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

    def test_create_edit_delete_song(self, caplog) -> None:
        """Test method used to create a new song,
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
        # with self.assertNoLogs(level=logging.WARNING) as cm: #TODO #25
        song_id = self.api.create_song(title, songcategory_id)
        assert song_id is not None

        ct_song = self.api.get_songs(song_id=song_id)[0]
        assert ct_song["name"] == title
        assert ct_song["author"] == ""
        assert ct_song["category"]["id"] == songcategory_id

        # 2. Edit Song title and check it exists with all params
        self.api.edit_song(song_id, title="Test_bezeichnung2")
        ct_song = self.api.get_songs(song_id=song_id)[0]
        assert ct_song["author"] == ""
        assert ct_song["name"] == "Test_bezeichnung2"

        # 3. Edit all fields and check it exists with all params
        data = {
            "bezeichnung": "Test_bezeichnung3",
            "songcategory_id": 1,
            "author": "Test_author",
            "copyright": "Test_copyright",
            "ccli": "Test_ccli",
            "practice_yn": 1,
        }
        self.api.edit_song(
            song_id=song_id,
            songcategory_id=data["songcategory_id"],
            title=data["bezeichnung"],
            author=data["author"],
            copyright=data["copyright"],
            ccli=data["ccli"],
            practice_yn=data["practice_yn"],
        )
        ct_song = self.api.get_songs(song_id=song_id)[0]
        assert ct_song["name"] == data["bezeichnung"]
        assert ct_song["category"]["id"] == data["songcategory_id"]
        assert ct_song["author"] == data["author"]
        assert ct_song["copyright"] == data["copyright"]
        assert ct_song["ccli"] == data["ccli"]
        assert ct_song["shouldPractice"] == data["practice_yn"]

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

    def test_add_remove_song_tag(self, caplog) -> None:
        """Test method used to add and remove the test tag to some song.

        Tag ID and Song ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS song_id 408 (sample_no_ct_attachement)
            and tag_id 53 (Test)

        self.api.ajax_song_last_update = None is required
            in order to clear the ajax song cache

        Returns: None
        """
        SAMPLE_SONG_ID = 408
        TEST_SONG_TAG = 53

        self.api.ajax_song_last_update = None
        assert self.api.contains_song_tag(SAMPLE_SONG_ID, TEST_SONG_TAG)
        caplog.clear()
        with caplog.at_level(logging.INFO):
            response = self.api.remove_song_tag(SAMPLE_SONG_ID, TEST_SONG_TAG)
        assert response.status_code == requests.codes.ok

        EXPECTED_MESSAGES = [
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint",
        ]
        assert caplog.messages == EXPECTED_MESSAGES

        self.api.ajax_song_last_update = None
        assert not self.api.contains_song_tag(SAMPLE_SONG_ID, TEST_SONG_TAG)

        self.api.ajax_song_last_update = None
        caplog.clear()
        with caplog.at_level(logging.INFO):
            response = self.api.add_song_tag(SAMPLE_SONG_ID, TEST_SONG_TAG)
        assert response.status_code == requests.codes.ok
        EXPECTED_MESSAGES = [
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint",
        ]
        assert caplog.messages == EXPECTED_MESSAGES

        self.api.ajax_song_last_update = None
        assert self.api.contains_song_tag(SAMPLE_SONG_ID, TEST_SONG_TAG)

    def test_get_song_tag_original(self) -> None:
        """Cchek song tag can be retrieved and returned as original."""
        SAMPLE_SONG_ID = 408
        result = self.api.get_song_tags(song_id=SAMPLE_SONG_ID)
        EXPECTED_TAG = 53
        assert EXPECTED_TAG in result

    def test_get_song_tag_id_dict(self) -> None:
        """Check song tag can be retrieved and returned as id dict."""
        SAMPLE_SONG_ID = 408
        result = self.api.get_song_tags(song_id=SAMPLE_SONG_ID, rtype="id_dict")
        EXPECTED_MIN_RESULT = {53: "Test"}
        assert all(item in result.items() for item in EXPECTED_MIN_RESULT.items())
        assert all(key in result for key in EXPECTED_MIN_RESULT)

    def test_get_song_tag_name_dict(self) -> None:
        """Check song tag can be retrieved and returned as name dict."""
        SAMPLE_SONG_ID = 408
        result = self.api.get_song_tags(song_id=SAMPLE_SONG_ID, rtype="name_dict")
        EXPECTED_MIN_RESULT = {"Test": 53}
        assert all(item in result.items() for item in EXPECTED_MIN_RESULT.items())

    def test_get_songs_with_tag(self) -> None:
        """Test method to check if fetching all songs with a specific tag works.

        songId and tag_id will vary depending on the server used
        On ELKW1610.KRZ.TOOLS song ID 408 is tagged with 53 "Test"
        :return:
        """
        SAMPLE_TAG_ID = 53
        SAMPLE_SONG_ID = 408

        self.api.ajax_song_last_update = None
        result = self.api.get_songs_by_tag(SAMPLE_TAG_ID)
        result_ids = [song["id"] for song in result]
        assert SAMPLE_SONG_ID in result_ids

    def test_get_song_source_map(self) -> None:
        """Checks respective method returns some data.

        On ELKW1610.KRZ.TOOLS there are at least two song sources configures
        """
        result = self.api.get_song_source_map()
        assert len(result) > 1
        assert all(isinstance(item, dict) for item in result.values())

    def test_lookup_song_source_as_id(self, caplog) -> None:
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
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint",
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
            "source_id": next(
                iter(SAMPLE_SOURCE.values())
            ),  # using shortname on purpse
            "source_ref": "source_ref",
            "tonality": "tonality",
            "bpm": "bpm",
            "beat": "beat",
            "length_min": 1,
            "length_sec": 2,
            "note": "note",
        }
        was_applied = self.api.edit_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id, **SAMPLE_PARAMS
        )
        assert was_applied
        created_arrangement = self.api.get_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id
        )
        assert created_arrangement["name"] == SAMPLE_ARRANGEMENT_NAME2
        assert created_arrangement["sourceName"] == next(iter(SAMPLE_SOURCE.values()))

        # edit2 - source as key id
        SAMPLE_PARAMS_SHORT = {
            "source_id": int(next(iter(SAMPLE_SOURCE.keys()))),
        }
        was_applied = self.api.edit_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id, **SAMPLE_PARAMS_SHORT
        )
        assert was_applied
        created_arrangement = self.api.get_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id
        )
        assert created_arrangement["sourceName"] == next(iter(SAMPLE_SOURCE.values()))
        assert (
            created_arrangement["duration"]
            == SAMPLE_PARAMS["length_min"] * 60 + SAMPLE_PARAMS["length_sec"]
        )

        # delete
        was_deleted = self.api.delete_song_arrangement(
            song_id=SAMPLE_SONG_ID, arrangement_id=arrangement_id
        )
        assert was_deleted
