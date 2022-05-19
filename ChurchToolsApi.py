import json
import logging
import os

import requests


class ChurchToolsApi:
    def __init__(self, domain):
        self.domain = domain

    def login_ct_ajax_api(self, user="beamer_maki@evang-kirche-baiersbronn.de", pswd=""):
        """
        Login function using AJAX with Username and Password
        :param user: Username
        :param pswd: Password - default safed in secure.token.user dict for tests
        :return: if login successful
        """
        self.session = requests.Session()
        login_url = self.domain + '/?q=login/ajax&func=login'
        data = {'email': user, 'password': pswd}
        self.session.post(url=login_url, data=data)
        #TODO return success

    def login_ct_rest_api(self, login_token):
        """
        Authorization: Login<token>
        If you want to authorized a request, you need to provide a Login Token as
        Authorization header in the format {Authorization: Login<token>}
        Login Tokens are generated in "Berechtigungen" of User Settings
        :param login_token: token to be used for login into CT
        :return: if login successful
        """

        session = requests.Session()
        login_url = self.domain + '/api/whoami'
        headers = {"Authorization": 'Login ' + login_token}
        response = session.get(url=login_url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            logging.info('Login Successful as {}'.format(response_content['data']['email']))
            self.session = session
        else:
            logging.warning("Login failed with {}".format(response.content.decode()))

        #TODO return success

    def get_ct_csrf_token(self):
        """
        Requests CSRF Token https://hilfe.church.tools/wiki/0/API-CSRF
        This method was created when debugging file upload but was no longer required later on
        :param session:
        :return: str token
        """
        url = self.domain + '/api/csrftoken'
        headers = {
            'accept': 'application/json',
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            csrf_token = json.loads(response.content)["data"]
            logging.info("CSRF Token erfolgreich abgerufen {}".format(csrf_token))
            return csrf_token
        else:
            logging.warning("CSRF Token not updated because of Response {}".format(response.content.decode()))

    def check_connection_ajax(self):
        """
        Checks whether a successful connection with the given token can be initiated using the legacy AJAX API
        :return:
        """
        url = self.domain + '/?q=churchservice/ajax&func=getAllFacts'
        headers = {
            'accept': 'application/json'
        }
        response = self.session.post(url=url, headers=headers)
        if response.status_code == 200:
            print("Response Test Connection erfolgreich")

    def get_songs(self, song_id=None):
        """ Gets list of all songs from the server
        :param song_id: optional filter by song id
        :return JSON Response Aller Lieder aus CT
        """
        url = self.domain + '/api/songs'
        if song_id is not None:
            url = url + '/{}'.format(song_id)
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            response_content = json.loads(response.content)['data']
            logging.debug("Response successful {}".format(response_content))
            return response_content

    def get_groups(self, group_id=None):
        """ Gets list of all groups
        :param group_id: optional filter by group id
        :return dict mit allen Gruppen
        """
        url = self.domain + '/api/groups'
        if group_id is not None:
            url = url + '/{}'.format(group_id)
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            response_content = json.loads(response.content)['data']
            logging.debug("Response successful {}".format(response_content))
            return response_content

    def file_upload(self, filenamepath_for_upload, domain_type='song_arrangement', domain_identifier=394,
                    file_name=None,
                    overwrite=False):
        """
        Helper function to upload an attachment to any module of ChurchTools

        :param filenamepath_for_upload: file to be opened e.g. with open('media/pinguin.png', 'rb')
        :param domain_type:  The domain type. Currently supported are 'avatar', 'groupimage', 'logo', 'attatchments',
         'html_template', 'service', 'song_arrangement', 'importtable', 'person', 'familyavatar', 'wiki_.?'.
        :param domain_identifier: ID of the object in ChurchTools
        :param file_name: optional file name - if not specified the one from the file is used
        :param overwrite: if true delete existing file before upload of new one to replace it's content instead of creating a copy
        :return:
        """

        file_to_upload = open(filenamepath_for_upload, 'rb')

        url = '{}/api/files/{}/{}'.format(self.domain, domain_type, domain_identifier)

        if overwrite:
            logging.debug("deleting old file before download")
            delete_file_name = file_to_upload.name if file_name is None else file_name
            self.file_delete(domain_type, domain_identifier, delete_file_name)

        # add files as files form data with dict using 'files[]' as key and (tuple of filename and fileobject)
        if file_name is None:
            files = {'files[]': (file_to_upload.name.split('/')[-1], file_to_upload)}
        else:
            files = {'files[]': (file_name, file_to_upload)}

        response = self.session.post(url=url, files=files)
        file_to_upload.close()

        """
        # Issues with HEADERS in Request module when using non standard 'files[]' key in POST Request
        # Workaround for ChurchTools - generate session with /api/whoami GET request and reuse it
        # Requests module usually automatically completes required header Params e.g. Content-Type ...
        # in case manual header e.g. for AUTH is used, headers don't auto complete
        # and server rejects messsages or data is ommited 
        # Error Code 500 is also missing in API documentation
        
        headers = {'Authorization': 'Login GEHEIM'}
        response_test = requests.post(url=url, headers=headers, files=files)
        #> this fails !
        """

        if response.status_code == 200:
            response_content = json.loads(response.content)
            logging.debug("Upload successful {}".format(response_content))
        else:
            logging.warning(response.content.decode())

    def file_delete(self, domain_type='song_arrangement', domain_identifier=394, filename_for_delete=None):
        """
        Helper function to delete ALL attachments of any specified module of ChurchTools#
        Downloads all existing files to tmp and reuploads them in case filename_for_delete is specified

        :param domain_type:  The domain type. Currently supported are 'avatar', 'groupimage', 'logo', 'attatchments',
         'html_template', 'service', 'song_arrangement', 'importtable', 'person', 'familyavatar', 'wiki_.?'.
         defaults to song_arrangement for testing
        :param domain_identifier: ID of the object in ChurchTools defaults to test song
        :param filename_for_delete: name of the file to be deleted - all others will reupload
        :return:
        """
        url = self.domain + '/api/files/{}/{}'.format(domain_type, domain_identifier)

        if filename_for_delete is not None:

            response = self.session.get(url=url)
            online_files = [(item["id"], item['name'], item['fileUrl']) for item in
                            json.loads(response.content)['data']]

            for current_file in online_files:
                current_id = current_file[0]
                current_name = current_file[1]
                current_url = current_file[2]
                if current_name != filename_for_delete:
                    response = self.session.get(current_file[2])
                    file_path_name = "tmp/{}_{}".format(current_id, current_name)
                    temp_file = open(file_path_name, "wb")
                    temp_file.write(response.content)
                    temp_file.close()

        # Delete all Files for the id online
        response = self.session.delete(url=url)

        # Recover Local Files with new upload and delete local copy from tmp
        if filename_for_delete is not None:
            local_files = os.listdir('tmp')
            for current_file in local_files:
                file_name = ''.join((current_file.split("_")[1:]))
                self.file_upload('tmp/{}'.format(current_file), file_name=file_name)
                os.remove('tmp/{}'.format(current_file))