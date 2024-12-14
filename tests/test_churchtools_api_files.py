"""module test files."""
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


class TestChurchtoolsApiFiles(TestsChurchToolsApiAbstract):
    """Test for Files."""

    def test_file_upload_replace_delete(self) -> None:
        """Checks procedures around file upload, replace and delete.

        IMPORTANT - This test method and the parameters used depend on target system!
        0. Clean and delete files in test
        1. Tries 3 uploads to the test song with ID 408 and arrangement 417
        Adds the same file again without overwrite - should exist twice
        2. Reupload pinguin.png using overwrite which will remove both old
            files but keep one
        3. Overwrite without existing file
        3.b Try overwriting again and check that number of files does not increase
        4. Delete only one file
        cleanup delete all files
        """
        SAMPLE_SONG_ID = 408
        SAMPLE_ARANGEMENT_ID = 417

        # 0. Clean and delete files in test
        self.api.file_delete("song_arrangement", SAMPLE_ARANGEMENT_ID)
        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        assert (
            song["arrangements"][0]["id"] == SAMPLE_ARANGEMENT_ID
        ), "check that default arrangement exists"
        assert len(song["arrangements"][0]["files"]) == 0, "check that ono files exist"

        # 1. Tries 3 uploads to the test song with ID 408 and arrangement 417
        # Adds the same file again without overwrite - should exist twice
        self.api.file_upload(
            "samples/pinguin.png", "song_arrangement", SAMPLE_ARANGEMENT_ID
        )
        self.api.file_upload(
            "samples/pinguin_shell.png",
            "song_arrangement",
            SAMPLE_ARANGEMENT_ID,
            "pinguin_shell_rename.png",
        )
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            SAMPLE_ARANGEMENT_ID,
            "pinguin.png",
        )

        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        assert isinstance(
            song, dict
        ), "Should be a single song instead of list of songs"
        assert (
            song["arrangements"][0]["id"] == SAMPLE_ARANGEMENT_ID
        ), "check that default arrangement exsits"
        EXPECTED_NUMBER_OF_FILES = 3
        assert (
            len(song["arrangements"][0]["files"]) == EXPECTED_NUMBER_OF_FILES
        ), "check that only the 3 test attachments exist"
        filenames = [i["name"] for i in song["arrangements"][0]["files"]]
        filenames_target = ["pinguin.png", "pinguin_shell_rename.png", "pinguin.png"]
        assert filenames == filenames_target

        # 2. Reupload pinguin.png using overwrite which will remove both old
        # files but keep one
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            SAMPLE_ARANGEMENT_ID,
            "pinguin.png",
            overwrite=True,
        )
        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        EXPECTED_NUMBER_OF_FILES = 2
        assert (
            len(song["arrangements"][0]["files"]) == EXPECTED_NUMBER_OF_FILES
        ), "check that overwrite is applied on upload"

        # 3. Overwrite without existing file
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            417,
            "pinguin2.png",
            overwrite=True,
        )
        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        EXPECTED_NUMBER_OF_FILES = 3
        assert (
            len(song["arrangements"][0]["files"]) == EXPECTED_NUMBER_OF_FILES
        ), "check that both file with overwrite of new file"

        # 3.b Try overwriting again and check that number of files does not
        # increase
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            417,
            "pinguin.png",
            overwrite=True,
        )
        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        EXPECTED_NUMBER_OF_FILES = 3
        assert (
            len(song["arrangements"][0]["files"]) == EXPECTED_NUMBER_OF_FILES
        ), "check that still only 3 file exists"

        # 4. Delete only one file
        self.api.file_delete("song_arrangement", SAMPLE_ARANGEMENT_ID, "pinguin.png")
        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        EXPECTED_NUMBER_OF_FILES = 2
        assert (
            len(song["arrangements"][0]["files"]) == EXPECTED_NUMBER_OF_FILES
        ), "check that still only 2 file exists"

        # cleanup delete all files
        self.api.file_delete("song_arrangement", SAMPLE_ARANGEMENT_ID)
        song = self.api.get_songs(song_id=SAMPLE_SONG_ID)[0]
        assert (
            len(song["arrangements"][0]["files"]) == 0
        ), "check that files are deleted"

    def test_file_download(self) -> None:
        """Test of file_download and file_download_from_url.

        on https://elkw1610.krz.tools on any song
        IDs  vary depending on the server used
        On ELKW1610.KRZ.TOOLS song ID 762 has arrangement 774 does exist.

        Uploads a test file
        downloads the file via same ID
        checks that file and content match
        deletes test file
        """
        test_id = 762

        self.api.file_upload("samples/test.txt", "song_arrangement", test_id)

        filePath = Path("downloads/test.txt")

        filePath.unlink(missing_ok=True)

        self.api.file_download("test.txt", "song_arrangement", test_id)
        with filePath.open() as file:
            download_text = file.read()
        assert download_text == "TEST CONTENT"

        self.api.file_delete("song_arrangement", test_id, "test.txt")
        filePath.unlink()
