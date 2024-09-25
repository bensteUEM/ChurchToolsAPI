import ast
import logging
import os
import unittest
from datetime import datetime, timedelta

from churchtools_api.churchtools_api import ChurchToolsApi


class TestsChurchToolsApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestsChurchToolsApi, self).__init__(*args, **kwargs)

        if 'CT_TOKEN' in os.environ:
            self.ct_token = os.environ['CT_TOKEN']
            self.ct_domain = os.environ['CT_DOMAIN']
            users_string = os.environ['CT_USERS']
            self.ct_users = ast.literal_eval(users_string)
            logging.info(
                'using connection details provided with ENV variables')
        else:
            from secure.config import ct_token
            self.ct_token = ct_token
            from secure.config import ct_domain
            self.ct_domain = ct_domain
            from secure.config import ct_users
            self.ct_users = ct_users
            logging.info(
                'using connection details provided from secrets folder')

        self.api = ChurchToolsApi(
            domain=self.ct_domain,
            ct_token=self.ct_token)
        logging.basicConfig(filename='logs/TestsChurchToolsApi.log', encoding='utf-8',
                            format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                            level=logging.DEBUG)
        logging.info("Executing Tests RUN")

    def tearDown(self):
        """
        Destroy the session after test execution to avoid resource issues
        :return:
        """
        self.api.session.close()

    def test_init_userpwd(self):
        """
        Tries to create a login with churchTools using specified username and password
        :return:
        """
        if self.api.session is not None:
            self.api.session.close()
        username = list(self.ct_users.keys())[0]
        password = list(self.ct_users.values())[0]
        ct_api = ChurchToolsApi(
            self.ct_domain,
            ct_user=username,
            ct_password=password)
        self.assertIsNotNone(ct_api)
        ct_api.session.close()

    def test_login_ct_rest_api(self):
        """
        Checks that Userlogin using REST is working with provided TOKEN
        :return:
        """
        if self.api.session is not None:
            self.api.session.close()
        result = self.api.login_ct_rest_api(ct_token=self.ct_token)
        self.assertTrue(result)

        username = list(self.ct_users.keys())[0]
        password = list(self.ct_users.values())[0]
        if self.api.session is not None:
            self.api.session.close()
        result = self.api.login_ct_rest_api(
            ct_user=username, ct_password=password)
        self.assertTrue(result)

    def test_get_ct_csrf_token(self):
        """
        Test checks that a CSRF token can be requested using the current API status
        :return:
        """
        token = self.api.get_ct_csrf_token()
        self.assertGreater(
            len(token),
            0,
            "Token should be more than one letter but changes each time")

    def test_check_connection_ajax(self):
        """
        Test checks that a connection can be established using the AJAX endpoints with current session / ct_api
        :return:
        """
        result = self.api.check_connection_ajax()
        self.assertTrue(result)

    def test_get_persons(self):
        """
        Tries to get all and a single person from the server
        Be aware that only ct_users that are visible to the user associated with the login token can be viewed!
        On any elkw.KRZ.TOOLS personId 1 'firstName' starts with 'Ben' and more than 10 ct_users exist(13. Jan 2023)
        :return:
        """

        personId = 1
        result1 = self.api.get_persons()
        self.assertIsInstance(result1, list)
        self.assertIsInstance(result1[0], dict)
        self.assertGreater(len(result1), 10)

        result2 = self.api.get_persons(ids=[personId])
        self.assertIsInstance(result2, list)
        self.assertIsInstance(result2[0], dict)
        self.assertEqual(result2[0]['firstName'][0:3], 'Ben')

        result3 = self.api.get_persons(returnAsDict=True)
        self.assertIsInstance(result3, dict)

        result4 = self.api.get_persons(returnAsDict=False)
        self.assertIsInstance(result4, list)

    def test_get_songs(self) -> None:
        """
        1. Test requests all songs and checks that result has more than 10 elements (hence default pagination works)
        2. Test requests song 2034 and checks that result matches "sample"

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        test_song_id = 2034

        songs = self.api.get_songs()
        self.assertGreater(len(songs), 10)

        song = self.api.get_songs(song_id=test_song_id)[0]
        self.assertEqual(song["id"], 2034)
        self.assertEqual(song["name"], "sample")

    def test_get_song_ajax(self):
        """
        Testing legacy AJAX API to request one specific song
        1. Test requests song 408 and checks that result matches Test song
        IMPORTANT - This test method and the parameters used depend on the target system!
        :return:
        """
        test_song_id = 408
        song = self.api.get_song_ajax(song_id=test_song_id)
        self.assertIsInstance(song, dict)
        self.assertEqual(len(song), 14)

        self.assertEqual(int(song['id']), test_song_id)
        self.assertEqual(song['bezeichnung'], 'Test')

    def test_get_song_category_map(self):
        """
        Checks that a dict with respective known values is returned when requesting song categories
        IMPORTANT - This test method and the parameters used depend on the target system!
        Requires the connected test system to have a category "Test" mapped as ID 13 (or changed if other system)
        :return:
        """

        song_catgegory_dict = self.api.get_song_category_map()
        self.assertEqual(song_catgegory_dict['Test'], 13)

    def test_get_groups(self) -> None:
        """
        1. Test requests all groups and checks that result has more than 10 elements (hence default pagination works)
        2. Test requests group 103 and checks that result matches Test song

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """

        groups = self.api.get_groups()
        self.assertTrue(isinstance(groups, list))
        self.assertTrue(isinstance(groups[0], dict))
        self.assertGreater(len(groups), 10)

        group = self.api.get_groups(group_id=103)
        self.assertEqual(group["id"], 103)
        self.assertEqual(group["name"], "TestGruppe")

    def test_get_groups_hierarchies(self):
        """
        Checks that the list of group hierarchies can be retrieved and each
        element contains the keys 'groupId', 'parents' and 'children'.
        The list should be accessible as dict using groupID as key
        :return:
        """
        hierarchies = self.api.get_groups_hierarchies()
        self.assertIsInstance(hierarchies, dict)
        for hierarchy in hierarchies.values():
            self.assertTrue('groupId' in hierarchy)
            self.assertTrue('parents' in hierarchy)
            self.assertTrue('children' in hierarchy)

    def test_get_group_statistics(self) -> None:
        """
        Checks that the statistics for a group can be retrieved and certain keys
        exist in the dict.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103

        stats = self.api.get_group_statistics(group_id=SAMPLE_GROUP_ID)
        self.assertIsNotNone(stats)
        self.assertIn("unfiltered", stats)
        self.assertIn("freePlaces", stats["unfiltered"])
        self.assertIn("takenPlaces", stats["unfiltered"])

    def test_get_grouptypes(self):
        """
        1. Check that the list of grouptypes can be retrieved and each element contains the keys 'id' and 'name'.
        2. Check that a single grouptype can be retrieved and id and name are matching.
        IMPORTANT - This test method and the parameters used depend on the target system!

        :return:
        """
        # multiple group types
        grouptypes = self.api.get_grouptypes()
        self.assertIsInstance(grouptypes, dict)
        self.assertGreater(len(grouptypes), 2)
        for grouptype in grouptypes.values():
            self.assertTrue('id' in grouptype)
            self.assertTrue('name' in grouptype)

        # one type only
        grouptypes = self.api.get_grouptypes(grouptype_id=2)
        self.assertEqual(len(grouptypes), 1)
        for grouptype in grouptypes.values():
            self.assertTrue('id' in grouptype)
            self.assertTrue('name' in grouptype)
            self.assertEqual(grouptype['id'], 2)
            self.assertEqual(grouptype['name'], 'Dienst')

    def test_get_group_permissions(self):
        """
        IMPORTANT - This test method and the parameters used depend on the target system!
        Checks that the permissions for a group can be retrieved and matches the test permissions.
        :return:
        """
        permissions = self.api.get_group_permissions(group_id=103)
        self.assertEqual(permissions['churchdb']['+see group'], 2)
        self.assertTrue(permissions['churchdb']['+edit group infos'])

    def test_create_and_delete_group(self):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

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
        self.assertIsNotNone(group1)
        self.assertEqual(group1["name"], SAMPLE_GROUP_NAME)
        self.assertEqual(group1["information"]["groupTypeId"], SAMPLE_NEW_GROUP_TYPE)
        self.assertEqual(group1["information"]["groupStatusId"], SAMPLE_GROUP_STATUS_ID)

        SAMPLE_GROUP_NAME2 = "TestGroup With Campus And Superior"
        group2 = self.api.create_group(
            SAMPLE_GROUP_NAME2,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            campus_id=SAMPLE_CAMPUS_ID,
            superior_group_id=group1["id"],
        )
        self.assertIsNotNone(group2)
        self.assertEqual(group2["name"], SAMPLE_GROUP_NAME2)
        self.assertEqual(group2["information"]["groupTypeId"], SAMPLE_NEW_GROUP_TYPE)
        self.assertEqual(group2["information"]["groupStatusId"], SAMPLE_GROUP_STATUS_ID)
        self.assertEqual(group2["information"]["campusId"], SAMPLE_CAMPUS_ID)

        group3 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
        )
        self.assertIsNone(group3)

        group3 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            force=True,
        )
        self.assertIsNotNone(group3)
        self.assertEqual(group3["name"], SAMPLE_GROUP_NAME)
        self.assertEqual(group3["information"]["groupTypeId"], SAMPLE_NEW_GROUP_TYPE)
        self.assertEqual(group3["information"]["groupStatusId"], SAMPLE_GROUP_STATUS_ID)

        # cleanup after testing
        ret = self.api.delete_group(group_id=group1["id"])
        self.assertTrue(ret)

        ret = self.api.delete_group(group_id=group2["id"])
        self.assertTrue(ret)

        ret = self.api.delete_group(group_id=group3["id"])
        self.assertTrue(ret)

    def test_update_group(self):
        """
        IMPORTANT - This test method and the parameters used depend on the target system!
        The user needs to be able to change group information - usually "Leiter" permission enables this

        Checks that a field in a group can be set to some value and the returned group has this field value set.
        Also cleans the field after executing the test
        :return:
        """
        test_group_id = 103
        data = {"note": "TestNote - if this exists an automated test case failed"}
        group = self.api.update_group(group_id=test_group_id, data=data)
        self.assertEqual(group['information']['note'], data['note'])

        group = self.api.update_group(
            group_id=test_group_id, data={"note": ""})
        group = self.api.get_groups(group_id=test_group_id)
        self.assertEqual(group['information']['note'], '')

    def test_get_group_members(self) -> None:
        """Checks if group members can be retrieved from the group and filtering
        for role ids works.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_GROUPTYPE_ROLE_ID = 16
        members = self.api.get_group_members(group_id=SAMPLE_GROUP_ID)

        self.assertIsNotNone(members)
        self.assertNotEqual(members, [])
        for member in members:
            self.assertIn("personId", member)

        members = self.api.get_group_members(
            group_id=SAMPLE_GROUP_ID, role_ids=[SAMPLE_GROUPTYPE_ROLE_ID]
        )
        self.assertIsNotNone(members)
        self.assertNotEqual(members, [])
        for member in members:
            self.assertIn("personId", member)
            self.assertEqual(member["groupTypeRoleId"], SAMPLE_GROUPTYPE_ROLE_ID)

    def test_get_groups_members(self) -> None:
        """Check that a list of groups is received when asking by person and optional role id

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
        self.assertIn(EXPECTED_GROUP_ID, compare_result)

        # 2a. person user and role - non lead - no group
        group_result = self.api.get_groups_members(
            person_ids=SAMPLE_PERSON_IDS, grouptype_role_ids=[SAMPLE_ROLE_ID_MEMBER]
        )
        self.assertEqual(len(group_result), 0)

        # 2b. person and role - lead and non lead
        group_result = self.api.get_groups_members(
            person_ids=SAMPLE_PERSON_IDS,
            groupTypeRoleId=[SAMPLE_ROLE_ID_LEAD, SAMPLE_ROLE_ID_MEMBER],
        )
        self.assertTrue(isinstance(group_result, list))
        self.assertGreater(len(group_result), 0)
        self.assertTrue(isinstance(group_result[0], dict))

        compare_result = [group["groupId"] for group in group_result]
        self.assertIn(EXPECTED_GROUP_ID, compare_result)

    def test_add_and_remove_group_members(self)->None:
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
        self.assertIsNotNone(member)
        self.assertEqual(member["personId"], SAMPLE_PERSON_ID)
        self.assertEqual(member["groupTypeRoleId"], SAMPLE_GROUPTYPE_ROLE_ID)
        self.assertEqual(member["groupMemberStatus"], "active")

        result = self.api.remove_group_member(
            group_id=SAMPLE_GROUP_ID, person_id=SAMPLE_PERSON_ID
        )
        self.assertTrue(result)

    def test_get_group_roles(self) -> None:
        """Checks if group roles can be retrieved from a group."""
        SAMPLE_GROUP_ID = 103
        roles = self.api.get_group_roles(group_id=SAMPLE_GROUP_ID)
        self.assertIsNotNone(roles)
        self.assertNotEqual(roles, [])
        for role in roles:
            self.assertIn("id", role)
            self.assertIn("groupTypeId", role)
            self.assertIn("name", role)

    def test_add_and_remove_parent_group(self) -> None:
        """Checks if a parent group can be added to and removed from a group.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_PARENT_GROUP_ID = 50
        result = self.api.add_parent_group(
            group_id=SAMPLE_GROUP_ID, parent_group_id=SAMPLE_PARENT_GROUP_ID
        )
        self.assertTrue(result)

        result = self.api.remove_parent_group(
            group_id=SAMPLE_GROUP_ID, parent_group_id=SAMPLE_PARENT_GROUP_ID
        )
        self.assertTrue(result)

    def test_get_global_permissions(self):
        """
        IMPORTANT - This test method and the parameters used depend on the target system!

        Checks that the global permissions for the current user can be retrieved
        and one core permission and one db permission matches the expected value.
        :return:
        """
        permissions = self.api.get_global_permissions()
        self.assertIn('churchcore', permissions.keys())
        self.assertIn('administer settings', permissions['churchcore'].keys())

        self.assertFalse(permissions['churchcore']['administer settings'])
        self.assertFalse(permissions['churchdb']['view birthdaylist'])
        self.assertTrue(permissions['churchwiki']['view'])

    def test_file_upload_replace_delete(self):
        """
        IMPORTANT - This test method and the parameters used depend on the target system!
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
        self.api.file_delete('song_arrangement', 417)
        song = self.api.get_songs(song_id=408)[0]
        self.assertEqual(
            song['arrangements'][0]['id'],
            417,
            'check that default arrangement exists')
        self.assertEqual(len(song['arrangements'][0]
                         ['files']), 0, 'check that ono files exist')

        # 1. Tries 3 uploads to the test song with ID 408 and arrangement 417
        # Adds the same file again without overwrite - should exist twice
        self.api.file_upload('samples/pinguin.png', "song_arrangement", 417)
        self.api.file_upload(
            'samples/pinguin_shell.png',
            "song_arrangement",
            417,
            'pinguin_shell_rename.png')
        self.api.file_upload(
            'samples/pinguin.png',
            "song_arrangement",
            417,
            'pinguin.png')

        song = self.api.get_songs(song_id=408)[0]
        self.assertIsInstance(
            song, dict, 'Should be a single song instead of list of songs')
        self.assertEqual(
            song['arrangements'][0]['id'],
            417,
            'check that default arrangement exsits')
        self.assertEqual(len(song['arrangements'][0]['files']),
                         3, 'check that only the 3 test attachments exist')
        filenames = [i['name'] for i in song['arrangements'][0]['files']]
        filenames_target = [
            'pinguin.png',
            'pinguin_shell_rename.png',
            'pinguin.png']
        self.assertEqual(filenames, filenames_target)

        # 2. Reupload pinguin.png using overwrite which will remove both old
        # files but keep one
        self.api.file_upload(
            'samples/pinguin.png',
            "song_arrangement",
            417,
            'pinguin.png',
            overwrite=True)
        song = self.api.get_songs(song_id=408)[0]
        self.assertEqual(len(song['arrangements'][0]['files']),
                         2, 'check that overwrite is applied on upload')

        # 3. Overwrite without existing file
        self.api.file_upload(
            'samples/pinguin.png',
            "song_arrangement",
            417,
            'pinguin2.png',
            overwrite=True)
        song = self.api.get_songs(song_id=408)[0]
        self.assertEqual(len(song['arrangements'][0]['files']),
                         3, 'check that both file with overwrite of new file')

        # 3.b Try overwriting again and check that number of files does not
        # increase
        self.api.file_upload(
            'samples/pinguin.png',
            "song_arrangement",
            417,
            'pinguin.png',
            overwrite=True)
        song = self.api.get_songs(song_id=408)[0]
        self.assertEqual(len(song['arrangements'][0]['files']),
                         3, 'check that still only 3 file exists')

        # 4. Delete only one file
        self.api.file_delete("song_arrangement", 417, "pinguin.png")
        song = self.api.get_songs(song_id=408)[0]
        self.assertEqual(len(song['arrangements'][0]['files']),
                         2, 'check that still only 2 file exists')

        # cleanup delete all files
        self.api.file_delete('song_arrangement', 417)
        song = self.api.get_songs(song_id=408)[0]
        self.assertEqual(
            len(song['arrangements'][0]['files']), 0, 'check that files are deleted')

    def test_create_edit_delete_song(self):
        """
        Test method used to create a new song, edit it's metadata and remove the song
        Does only test metadata not attachments or arrangements
        IMPORTANT - This test method and the parameters used depend on the target system!
        On ELKW1610.KRZ.TOOLS songcategory_id 13 is TEST
        :return:
        """
        title = 'Test_bezeichnung1'
        songcategory_id = 13

        # 1. Create Song after and check it exists with all params
        # with self.assertNoLogs(level=logging.WARNING) as cm: #TODO #25
        song_id = self.api.create_song(title, songcategory_id)
        self.assertIsNotNone(song_id)

        ct_song = self.api.get_songs(song_id=song_id)[0]
        self.assertEqual(ct_song['name'], title)
        self.assertEqual(ct_song['author'], '')
        self.assertEqual(ct_song['category']['id'], songcategory_id)

        # 2. Edit Song title and check it exists with all params
        self.api.edit_song(song_id, title='Test_bezeichnung2')
        ct_song = self.api.get_songs(song_id=song_id)[0]
        self.assertEqual(ct_song['author'], '')
        self.assertEqual(ct_song['name'], 'Test_bezeichnung2')

        # 3. Edit all fields and check it exists with all params
        data = {
            'bezeichnung': 'Test_bezeichnung3',
            'songcategory_id': 1,  # needs to exist does not matter which because deleted later
            'author': 'Test_author',
            'copyright': 'Test_copyright',
            'ccli': 'Test_ccli',
            'practice_yn': 1,
        }
        self.api.edit_song(song_id, data['songcategory_id'], data['bezeichnung'], data['author'], data['copyright'],
                           data['ccli'], data['practice_yn'])
        ct_song = self.api.get_songs(song_id=song_id)[0]
        self.assertEqual(ct_song['name'], data['bezeichnung'])
        self.assertEqual(ct_song['category']['id'], data['songcategory_id'])
        self.assertEqual(ct_song['author'], data['author'])
        self.assertEqual(ct_song['copyright'], data['copyright'])
        self.assertEqual(ct_song['ccli'], data['ccli'])
        self.assertEqual(ct_song['shouldPractice'], data['practice_yn'])

        # Delete Song
        self.api.delete_song(song_id)
        with self.assertLogs(level='INFO') as cm:
            ct_song = self.api.get_songs(song_id=song_id)
        messages = [
            "INFO:root:Did not find song ({}) with CODE 404".format(song_id)]
        self.assertEqual(messages, cm.output)
        self.assertIsNone(ct_song)

    def test_add_remove_song_tag(self):
        """
        Test method used to add and remove the test tag to some song
        Tag ID and Song ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS song_id 408 and tag_id 53
        self.api.ajax_song_last_update = None is required in order to clear the ajax song cache
        :return:
        """
        self.api.ajax_song_last_update = None
        self.assertTrue(self.api.contains_song_tag(408, 53))
        with self.assertNoLogs(level='INFO') as cm:
            response = self.api.remove_song_tag(408, 53)
        self.assertEqual(response.status_code, 200)

        self.api.ajax_song_last_update = None
        self.assertFalse(self.api.contains_song_tag(408, 53))

        self.api.ajax_song_last_update = None
        with self.assertNoLogs(level='INFO') as cm:
            response = self.api.add_song_tag(408, 53)
        self.assertEqual(response.status_code, 200)

        self.api.ajax_song_last_update = None
        self.assertTrue(self.api.contains_song_tag(408, 53))

    def test_get_songs_with_tag(self):
        """
        Test method to check if fetching all songs with a specific tag works
        songId and tag_id will vary depending on the server used
        On ELKW1610.KRZ.TOOLS song ID 408 is the first song with tag 53 "Test"
        :return:
        """
        tagId = 53
        songId = 408

        self.api.ajax_song_last_update = None
        result = self.api.get_songs_by_tag(tagId)
        self.assertEqual(songId, result[0]['id'])

    def test_file_download(self):
        """ Test of file_download and file_download_from_url on https://elkw1610.krz.tools on any song
        IDs  vary depending on the server used
        On ELKW1610.KRZ.TOOLS song ID 762 has arrangement 774 does exist

        Uploads a test file
        downloads the file via same ID
        checks that file and content match
        deletes test file
        """
        test_id = 762

        self.api.file_upload('samples/test.txt', 'song_arrangement', test_id)

        filePath = 'downloads/test.txt'
        if os.path.exists(filePath):
            os.remove(filePath)

        self.api.file_download('test.txt', 'song_arrangement', test_id)
        with open(filePath, "r") as file:
            download_text = file.read()
        self.assertEqual('TEST CONTENT', download_text)

        self.api.file_delete('song_arrangement', test_id, 'test.txt')
        if os.path.exists(filePath):
            os.remove(filePath)


if __name__ == '__main__':
    unittest.main()
