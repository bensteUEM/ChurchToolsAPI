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

    def test_get_groups(self) -> None:
        """1. Test requests all groups and checks that result has more than 50 elements (hence default pagination works)
        2. Test requests group 103 and checks that result matches Test song.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        groups = self.api.get_groups()
        assert isinstance(groups, list)
        assert isinstance(groups[0], dict)
        assert len(groups) > 10

        groups = self.api.get_groups(group_id=103)
        assert isinstance(groups, list)
        group = groups[0]
        assert isinstance(group, dict)
        assert group["id"] == 103
        assert group["name"] == "TestGruppe"

    def test_get_groups_hierarchies(self) -> None:
        """Checks that the list of group hierarchies can be retrieved and each
        element contains the keys 'groupId', 'parents' and 'children'.
        The list should be accessible as dict using groupID as key
        :return:
        """
        hierarchies = self.api.get_groups_hierarchies()
        assert isinstance(hierarchies, dict)
        for hierarchy in hierarchies.values():
            assert "groupId" in hierarchy
            assert "parents" in hierarchy
            assert "children" in hierarchy

    def test_get_group_statistics(self) -> None:
        """Checks that the statistics for a group can be retrieved and certain keys
        exist in the dict.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103

        stats = self.api.get_group_statistics(group_id=SAMPLE_GROUP_ID)
        assert stats is not None
        assert "unfiltered" in stats
        assert "freePlaces" in stats["unfiltered"]
        assert "takenPlaces" in stats["unfiltered"]

    def test_get_grouptypes(self) -> None:
        """1. Check that the list of grouptypes can be retrieved and each element contains the keys 'id' and 'name'.
        2. Check that a single grouptype can be retrieved and id and name are matching.
        IMPORTANT - This test method and the parameters used depend on the target system!

        :return:
        """
        # multiple group types
        grouptypes = self.api.get_grouptypes()
        assert isinstance(grouptypes, dict)
        assert len(grouptypes) > 2
        for grouptype in grouptypes.values():
            assert "id" in grouptype
            assert "name" in grouptype

        # one type only
        grouptypes = self.api.get_grouptypes(grouptype_id=2)
        assert len(grouptypes) == 1
        for grouptype in grouptypes.values():
            assert "id" in grouptype
            assert "name" in grouptype
            assert grouptype["id"] == 2
            assert grouptype["name"] == "Dienst"

    def test_get_group_permissions(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!
        Checks that the permissions for a group can be retrieved and matches the test permissions.
        :return:
        """
        permissions = self.api.get_group_permissions(group_id=103)
        assert permissions["churchdb"]["+see group"] == 2
        assert permissions["churchdb"]["+edit group infos"]

    def test_create_and_delete_group(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.

        1. Checks if groups can be created with minimal and optional parameters.
        2. Checks if a group can be created with a name of an existing group
           only when the 'force' parameter is set.
        3. Checks if groups can be deleted.
        :return:
        """
        SAMPLE_NEW_GROUP_TYPE = 2
        SAMPLE_GROUP_STATUS_ID = 1
        SAMPLE_CAMPUS_ID = 0
        SAMPLE_GROUP_NAME = "TestGroup"

        group1 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
        )
        assert group1 is not None
        assert group1["name"] == SAMPLE_GROUP_NAME
        assert group1["information"]["groupTypeId"] == SAMPLE_NEW_GROUP_TYPE
        assert group1["information"]["groupStatusId"] == SAMPLE_GROUP_STATUS_ID

        SAMPLE_GROUP_NAME2 = "TestGroup With Campus And Superior"
        group2 = self.api.create_group(
            SAMPLE_GROUP_NAME2,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            campus_id=SAMPLE_CAMPUS_ID,
            superior_group_id=group1["id"],
        )
        assert group2 is not None
        assert group2["name"] == SAMPLE_GROUP_NAME2
        assert group2["information"]["groupTypeId"] == SAMPLE_NEW_GROUP_TYPE
        assert group2["information"]["groupStatusId"] == SAMPLE_GROUP_STATUS_ID
        assert group2["information"]["campusId"] == SAMPLE_CAMPUS_ID

        group3 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
        )
        assert group3 is None

        group3 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            force=True,
        )
        assert group3 is not None
        assert group3["name"] == SAMPLE_GROUP_NAME
        assert group3["information"]["groupTypeId"] == SAMPLE_NEW_GROUP_TYPE
        assert group3["information"]["groupStatusId"] == SAMPLE_GROUP_STATUS_ID

        # cleanup after testing
        ret = self.api.delete_group(group_id=group1["id"])
        assert ret

        ret = self.api.delete_group(group_id=group2["id"])
        assert ret

        ret = self.api.delete_group(group_id=group3["id"])
        assert ret

    def test_update_group(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!
        The user needs to be able to change group information - usually "Leiter" permission enables this.

        Checks that a field in a group can be set to some value and the returned group has this field value set.
        Also cleans the field after executing the test
        :return:
        """
        SAMPLE_GROUP_ID = 103
        data = {"note": "TestNote - if this exists an automated test case failed"}
        group_update_result = self.api.update_group(group_id=SAMPLE_GROUP_ID, data=data)
        assert group_update_result["information"]["note"] == data["note"]

        group_update_result = self.api.update_group(
            group_id=SAMPLE_GROUP_ID,
            data={"note": ""},
        )
        groups = self.api.get_groups(group_id=SAMPLE_GROUP_ID)
        assert groups[0]["information"]["note"] == ""

    def test_get_group_members(self) -> None:
        """Checks if group members can be retrieved from the group and filtering
        for role ids works.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_GROUPTYPE_ROLE_ID = 16
        members = self.api.get_group_members(group_id=SAMPLE_GROUP_ID)

        assert members is not None
        assert members != []
        for member in members:
            assert "personId" in member

        members = self.api.get_group_members(
            group_id=SAMPLE_GROUP_ID,
            role_ids=[SAMPLE_GROUPTYPE_ROLE_ID],
        )
        assert members is not None
        assert members != []
        for member in members:
            assert "personId" in member
            assert member["groupTypeRoleId"] == SAMPLE_GROUPTYPE_ROLE_ID

    def test_get_groups_members(self) -> None:
        """Check that a list of groups is received when asking by person and optional role id.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_PERSON_IDS = [513]
        SAMPLE_ROLE_ID_LEAD = 16
        SAMPLE_ROLE_ID_MEMBER = 15
        EXPECTED_GROUP_ID = 103  # a services test group

        # 1. person only
        group_result = self.api.get_groups_members(person_ids=SAMPLE_PERSON_IDS)
        compare_result = [group["groupId"] for group in group_result]
        assert EXPECTED_GROUP_ID in compare_result

        # 2a. person user and role - non lead - no group
        group_result = self.api.get_groups_members(
            person_ids=SAMPLE_PERSON_IDS,
            grouptype_role_ids=[SAMPLE_ROLE_ID_MEMBER],
        )
        assert len(group_result) == 0

        # 2b. person and role - lead and non lead
        group_result = self.api.get_groups_members(
            person_ids=SAMPLE_PERSON_IDS,
            groupTypeRoleId=[SAMPLE_ROLE_ID_LEAD, SAMPLE_ROLE_ID_MEMBER],
        )
        assert isinstance(group_result, list)
        assert len(group_result) > 0
        assert isinstance(group_result[0], dict)

        compare_result = [group["groupId"] for group in group_result]
        assert EXPECTED_GROUP_ID in compare_result

        # 3. problematic result group_ids, grouptype_role_ids and person_id
        SAMPLE_GROUP_IDS = [99, 68, 93]
        SAMPLE_GROUPTYPE_ROLE_IDS = [9, 16]
        SAMPLE_PERSON_IDS = [54]

        result = self.api.get_groups_members(
            group_ids=SAMPLE_GROUP_IDS,
            grouptype_role_ids=SAMPLE_GROUPTYPE_ROLE_IDS,
            person_ids=SAMPLE_PERSON_IDS,
        )
        assert len(result) == 1

    def test_add_and_remove_group_members(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_PERSON_ID = 229
        SAMPLE_GROUPTYPE_ROLE_ID = 15

        member = self.api.add_group_member(
            group_id=SAMPLE_GROUP_ID,
            person_id=SAMPLE_PERSON_ID,
            grouptype_role_id=SAMPLE_GROUPTYPE_ROLE_ID,
            group_member_status="active",
        )
        assert member is not None
        assert member["personId"] == SAMPLE_PERSON_ID
        assert member["groupTypeRoleId"] == SAMPLE_GROUPTYPE_ROLE_ID
        assert member["groupMemberStatus"] == "active"

        result = self.api.remove_group_member(
            group_id=SAMPLE_GROUP_ID,
            person_id=SAMPLE_PERSON_ID,
        )
        assert result

    def test_get_group_roles(self) -> None:
        """Checks if group roles can be retrieved from a group."""
        SAMPLE_GROUP_ID = 103
        roles = self.api.get_group_roles(group_id=SAMPLE_GROUP_ID)
        assert roles is not None
        assert roles != []
        for role in roles:
            assert "id" in role
            assert "groupTypeId" in role
            assert "name" in role

    def test_add_and_remove_parent_group(self) -> None:
        """Checks if a parent group can be added to and removed from a group.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_PARENT_GROUP_ID = 50
        result = self.api.add_parent_group(
            group_id=SAMPLE_GROUP_ID,
            parent_group_id=SAMPLE_PARENT_GROUP_ID,
        )
        assert result

        result = self.api.remove_parent_group(
            group_id=SAMPLE_GROUP_ID,
            parent_group_id=SAMPLE_PARENT_GROUP_ID,
        )
        assert result

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
