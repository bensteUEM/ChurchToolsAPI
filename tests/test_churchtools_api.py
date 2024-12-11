import ast
import json
import logging
import logging.config
import os
import unittest
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


class TestsChurchToolsApi(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

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

    def tearDown(self) -> None:
        """Destroy the session after test execution to avoid resource issues
        :return:
        """
        self.api.session.close()

    def test_init_userpwd(self) -> None:
        """Tries to create a login with churchTools using specified username and password
        :return:
        """
        if self.api.session is not None:
            self.api.session.close()
        username = next(iter(self.ct_users.keys()))
        password = next(iter(self.ct_users.values()))
        ct_api = ChurchToolsApi(self.ct_domain, ct_user=username, ct_password=password)
        assert ct_api is not None
        ct_api.session.close()

    def test_login_ct_rest_api(self) -> None:
        """Checks that Userlogin using REST is working with provided TOKEN
        :return:
        """
        if self.api.session is not None:
            self.api.session.close()
        result = self.api.login_ct_rest_api(ct_token=self.ct_token)
        assert result

        username = next(iter(self.ct_users.keys()))
        password = next(iter(self.ct_users.values()))
        if self.api.session is not None:
            self.api.session.close()
        result = self.api.login_ct_rest_api(ct_user=username, ct_password=password)
        assert result

    def test_get_ct_csrf_token(self) -> None:
        """Test checks that a CSRF token can be requested using the current API status
        :return:
        """
        token = self.api.get_ct_csrf_token()
        assert (
            len(token) > 0
        ), "Token should be more than one letter but changes each time"

    def test_check_connection_ajax(self) -> None:
        """Test checks that a connection can be established using the AJAX endpoints with current session / ct_api
        :return:
        """
        result = self.api.check_connection_ajax()
        assert result

    def test_get_persons(self) -> None:
        """Tries to get all and a single person from the server
        Be aware that only ct_users that are visible to the user associated with the login token can be viewed!
        On any elkw.KRZ.TOOLS personId 1 'firstName' starts with 'Ben' and more than 50 ct_users exist(13. Jan 2023)
        :return:
        """
        personId = 1
        result1 = self.api.get_persons()
        assert isinstance(result1, list)
        assert isinstance(result1[0], dict)
        assert len(result1) > 50

        result2 = self.api.get_persons(ids=[personId])
        assert isinstance(result2, list)
        assert isinstance(result2[0], dict)
        assert result2[0]["firstName"][0:3] == "Ben"

        result3 = self.api.get_persons(returnAsDict=True)
        assert isinstance(result3, dict)

        result4 = self.api.get_persons(returnAsDict=False)
        assert isinstance(result4, list)

    def test_get_persons_masterdata(self) -> None:
        """Tries to retrieve metadata for persons module.
        Expected sections equal those that were available on ELKW1610.krz.tools on 4.Oct.2024.
        """
        EXPECTED_SECTIONS = {
            "roles",
            "ageGroups",
            "targetGroups",
            "groupTypes",
            "groupCategories",
            "groupStatuses",
            "departments",
            "statuses",
            "campuses",
            "contactLabels",
            "growPaths",
            "followUps",
            "followUpIntervals",
            "groupMeetingTemplates",
            "relationshipTypes",
            "sexes",
        }

        # all items
        result = self.api.get_persons_masterdata()
        assert isinstance(result, dict)
        assert set(result.keys()) == EXPECTED_SECTIONS

        for section in result.values():
            assert isinstance(section, list)
            for item in section:
                assert isinstance(item, dict)

        # only one type
        result = self.api.get_persons_masterdata(resultClass="sexes")
        assert isinstance(result, list)
        assert len(result) > 1
        assert isinstance(next(iter(result)), dict)

        # only one type as dict
        result = self.api.get_persons_masterdata(resultClass="sexes", returnAsDict=True)
        assert isinstance(result, dict)
        assert len(result) > 1
        assert isinstance(next(iter(result.keys())), int)
        assert isinstance(next(iter(result.values())), str)

    def test_get_options(self) -> None:
        """Checks that option fields can retrieved."""
        result = self.api.get_options()
        assert "sex" in result

    def test_get_persons_sex_id(self) -> None:
        """Tests that persons sexId can be retrieved and converted to a human readable gender.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        EXPECTED_RESULT = "sex.unknown"
        SAMPLE_USER_ID = 513

        person = self.api.get_persons(ids=[SAMPLE_USER_ID])
        gender_map = self.api.get_persons_masterdata(
            resultClass="sexes", returnAsDict=True
        )
        result = gender_map[person[0]["sexId"]]

        assert result == EXPECTED_RESULT

    def test_get_global_permissions(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Checks that the global permissions for the current user can be retrieved
        and one core permission and one db permission matches the expected value.
        :return:
        """
        permissions = self.api.get_global_permissions()
        assert "churchcore" in permissions
        assert "administer settings" in permissions["churchcore"]

        assert not permissions["churchcore"]["administer settings"]
        assert not permissions["churchdb"]["view birthdaylist"]
        assert permissions["churchwiki"]["view"]

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
        :return:
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


if __name__ == "__main__":
    unittest.main()
