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


class TestChurchtoolsApiFiles(TestsChurchToolsApiAbstract):
    def test_file_upload_replace_delete(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!
        0. Clean and delete files in test
        1. Tries 3 uploads to the test song with ID 408 and arrangement 417
        Adds the same file again without overwrite - should exist twice
        2. Reupload pinguin.png using overwrite which will remove both old files but keep one
        3. Overwrite without existing file
        3.b Try overwriting again and check that number of files does not increase
        4. Delete only one file
        cleanup delete all files
        """
        # 0. Clean and delete files in test
        self.api.file_delete("song_arrangement", 417)
        song = self.api.get_songs(song_id=408)[0]
        assert (
            song["arrangements"][0]["id"] == 417
        ), "check that default arrangement exists"
        assert len(song["arrangements"][0]["files"]) == 0, "check that ono files exist"

        # 1. Tries 3 uploads to the test song with ID 408 and arrangement 417
        # Adds the same file again without overwrite - should exist twice
        self.api.file_upload("samples/pinguin.png", "song_arrangement", 417)
        self.api.file_upload(
            "samples/pinguin_shell.png",
            "song_arrangement",
            417,
            "pinguin_shell_rename.png",
        )
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            417,
            "pinguin.png",
        )

        song = self.api.get_songs(song_id=408)[0]
        assert isinstance(
            song, dict
        ), "Should be a single song instead of list of songs"
        assert (
            song["arrangements"][0]["id"] == 417
        ), "check that default arrangement exsits"
        assert (
            len(song["arrangements"][0]["files"]) == 3
        ), "check that only the 3 test attachments exist"
        filenames = [i["name"] for i in song["arrangements"][0]["files"]]
        filenames_target = ["pinguin.png", "pinguin_shell_rename.png", "pinguin.png"]
        assert filenames == filenames_target

        # 2. Reupload pinguin.png using overwrite which will remove both old
        # files but keep one
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            417,
            "pinguin.png",
            overwrite=True,
        )
        song = self.api.get_songs(song_id=408)[0]
        assert (
            len(song["arrangements"][0]["files"]) == 2
        ), "check that overwrite is applied on upload"

        # 3. Overwrite without existing file
        self.api.file_upload(
            "samples/pinguin.png",
            "song_arrangement",
            417,
            "pinguin2.png",
            overwrite=True,
        )
        song = self.api.get_songs(song_id=408)[0]
        assert (
            len(song["arrangements"][0]["files"]) == 3
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
        song = self.api.get_songs(song_id=408)[0]
        assert (
            len(song["arrangements"][0]["files"]) == 3
        ), "check that still only 3 file exists"

        # 4. Delete only one file
        self.api.file_delete("song_arrangement", 417, "pinguin.png")
        song = self.api.get_songs(song_id=408)[0]
        assert (
            len(song["arrangements"][0]["files"]) == 2
        ), "check that still only 2 file exists"

        # cleanup delete all files
        self.api.file_delete("song_arrangement", 417)
        song = self.api.get_songs(song_id=408)[0]
        assert (
            len(song["arrangements"][0]["files"]) == 0
        ), "check that files are deleted"

    @pytest.mark.skip(reason="#122 - image options not applyable")
    def test_file_upload_delete_calendar_image(self):
        """Test which tries to upload a calendar_image to a calendar appointment.

        On ELKW1610.KRZ.TOOLS song ID 332233 exists as calendar appointment.
        """
        SAMPLE_CALENDAR_ID = 45
        SAMPLE_CALENDAR_APPOINTMENT_ID = 332233
        SAMPLE_IMAGE_PATH = Path("samples/pinguin.png")

        is_successful_created = self.api.file_upload(
            source_filepath=SAMPLE_IMAGE_PATH,
            domain_type="appointment_image",
            domain_identifier=SAMPLE_CALENDAR_APPOINTMENT_ID,
        )
        assert is_successful_created

        result_appointment = self.api.get_calendar_appointments(
            calendar_ids=[SAMPLE_CALENDAR_ID], appointment_id=SAMPLE_CALENDAR_APPOINTMENT_ID
        )
        assert result_appointment["image"] == SAMPLE_IMAGE_PATH.name

        is_successful_delete = self.api.file_delete(
            domain_type="appointment_image",
            domain_identifier=SAMPLE_CALENDAR_APPOINTMENT_ID,
        )
        assert is_successful_delete

    def test_file_download(self) -> None:
        """Test of file_download and file_download_from_url on https://elkw1610.krz.tools on any song
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
