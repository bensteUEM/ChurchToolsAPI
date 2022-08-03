import unittest

from ChurchToolsApi import *


class TestsChurchToolsApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestsChurchToolsApi, self).__init__(*args, **kwargs)
        from secure.defaults import domain as temp_domain
        self.api = ChurchToolsApi(temp_domain)
        logging.basicConfig(filename='logs/TestsChurchToolsApi.log', encoding='utf-8',
                            format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                            level=logging.DEBUG)
        logging.info("Executing Tests RUN")

    def test_login_ct_ajax_api(self):
        """
        Checks that Userlogin using AJAX is working with provided credentials
        :return:
        """
        from secure.secrets import users
        result = self.api.login_ct_ajax_api('beamer_maki@evang-kirche-baiersbronn.de',
                                            users['beamer_maki@evang-kirche-baiersbronn.de'])
        self.assertTrue(result)

    def test_login_ct_rest_api(self):
        """
        Checks that Userlogin using REST is working with provided TOKEN
        :return:
        """
        from secure.secrets import ct_token
        result = self.api.login_ct_rest_api(ct_token)
        self.assertTrue(result)

    def test_get_ct_csrf_token(self):
        """
        Test checks that a CSRF token can be requested using the current API status
        :return:
        """
        token = self.api.get_ct_csrf_token()
        self.assertGreater(len(token), 0, "Token should be more than one letter but changes each time")

    def test_check_connection_ajax(self):
        """
        Test checks that a connection can be established using the AJAX endpoints with current session / api
        :return:
        """
        result = self.api.check_connection_ajax()
        self.assertTrue(result)

    def test_get_songs(self):
        """
        1. Test requests all songs and checks that result has more than 10 elements (hence default pagination works)
        2. Test requests song 383 and checks that result matches Test song
        :return:
        """
        songs = self.api.get_songs()
        self.assertGreater(len(songs), 10)

        song = self.api.get_songs(song_id=408)
        self.assertEqual(song['id'], 408)
        self.assertEqual(song['name'], 'Test')

    def test_get_song_category_map(self):
        """
        Checks that a dict with respective known values is returned when requesting song categories
        Requires the connected test system to have a category "Test" mapped as ID 13 (or changed if other system)
        :return:
        """

        song_catgegory_dict = self.api.get_song_category_map()
        self.assertEqual(song_catgegory_dict['Test'], 13)

    def test_get_groups(self):
        """
        1. Test requests all groups and checks that result has more than 10 elements (hence default pagination works)
        2. Test requests group 103 and checks that result matches Test song
        :return:
        """

        groups = self.api.get_groups()
        self.assertGreater(len(groups), 10)

        group = self.api.get_groups(group_id=103)
        self.assertEqual(group['id'], 103)
        self.assertEqual(group['name'], 'TestGruppe')

    def test_file_upload_replace_delete(self):
        """
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
        song = self.api.get_songs(song_id=408)
        self.assertEqual(song['arrangements'][0]['id'], 417, 'check that default arrangement exists')
        self.assertEqual(len(song['arrangements'][0]['files']), 0, 'check that ono files exist')

        # 1. Tries 3 uploads to the test song with ID 408 and arrangement 417
        # Adds the same file again without overwrite - should exist twice
        self.api.file_upload('media/pinguin.png', "song_arrangement", 417)
        self.api.file_upload('media/pinguin_shell.png', "song_arrangement", 417, 'pinguin_shell_rename.png')
        self.api.file_upload('media/pinguin.png', "song_arrangement", 417, 'pinguin.png')

        song = self.api.get_songs(song_id=408)
        self.assertIsInstance(song, dict, 'Should be a single song instead of list of songs')
        self.assertEqual(song['arrangements'][0]['id'], 417, 'check that default arrangement exsits')
        self.assertEqual(len(song['arrangements'][0]['files']), 3, 'check that only the 3 test attachments exist')
        filenames = [i['name'] for i in song['arrangements'][0]['files']]
        filenames_target = ['pinguin.png', 'pinguin_shell_rename.png', 'pinguin.png']
        self.assertEqual(filenames, filenames_target)

        # 2. Reupload pinguin.png using overwrite which will remove both old files but keep one
        self.api.file_upload('media/pinguin.png', "song_arrangement", 417, 'pinguin.png', overwrite=True)
        song = self.api.get_songs(song_id=408)
        self.assertEqual(len(song['arrangements'][0]['files']), 2, 'check that overwrite is applied on upload')

        # 3. Overwrite without existing file
        self.api.file_upload('media/pinguin.png', "song_arrangement", 417, 'pinguin2.png', overwrite=True)
        song = self.api.get_songs(song_id=408)
        self.assertEqual(len(song['arrangements'][0]['files']), 3, 'check that both file with overwrite of new file')

        # 3.b Try overwriting again and check that number of files does not increase
        self.api.file_upload('media/pinguin.png', "song_arrangement", 417, 'pinguin.png', overwrite=True)
        song = self.api.get_songs(song_id=408)
        self.assertEqual(len(song['arrangements'][0]['files']), 3, 'check that still only 3 file exists')

        # 4. Delete only one file
        self.api.file_delete("song_arrangement", 417, "pinguin.png")
        song = self.api.get_songs(song_id=408)
        self.assertEqual(len(song['arrangements'][0]['files']), 2, 'check that still only 2 file exists')

        # cleanup delete all files
        self.api.file_delete('song_arrangement', 417)
        song = self.api.get_songs(song_id=408)
        self.assertEqual(len(song['arrangements'][0]['files']), 0, 'check that files are deleted')

    def test_create_edit_delete_song(self):
        """
        Test method used to create a new song, edit it's metadata and remove the song
        Does only test metadata not attachments or arrangements
        On ELKW1610.KRZ.TOOLS songcategory_id 13 ist TEST
        :return:
        """
        title = 'Test_bezeichnung1'
        songcategory_id = 13

        # 1. Create Song after and check it exists with all params
        song_id = self.api.create_song(title, songcategory_id)

        ct_song = self.api.get_songs(song_id=song_id)
        self.assertEqual(ct_song['name'], title)
        self.assertEqual(ct_song['author'], '')
        self.assertEqual(ct_song['category']['id'], songcategory_id)

        # 2. Edit Song title and check it exists with all params
        self.api.edit_song(song_id, title='Test_bezeichnung2')
        ct_song = self.api.get_songs(song_id=song_id)
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
        ct_song = self.api.get_songs(song_id=song_id)
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
        On ELKW1610.KRZ.TOOLS song_id 408 and tag_id 34
        :return:
        """
        self.assertTrue(self.api.contains_song_tag(408, 34))
        with self.assertNoLogs(level='INFO') as cm:
            response = self.api.remove_song_tag(408, 34)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(self.api.contains_song_tag(408, 34))

        with self.assertNoLogs(level='INFO') as cm:
            response = self.api.add_song_tag(408, 34)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.api.contains_song_tag(408, 34))

    def test_get_songs_with_tag(self):
        """
        Test method to check if fetching all songs with a specific tag works
        :return:
        """
        result = self.api.get_songs_with_tag(34)
        self.assertEqual(408, result[0]['id'])


if __name__ == '__main__':
    unittest.main()
