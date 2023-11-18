import ast
import logging
import os
import unittest
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
