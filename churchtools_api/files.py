import json
import logging
import os

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)

class ChurchToolsApiFiles(ChurchToolsApiAbstract):
    """ Part definition of ChurchToolsApi which focuses on files

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def file_upload(self, source_filepath, domain_type,
                    domain_identifier, custom_file_name=None, overwrite=False):
        """
        Helper function to upload an attachment to any module of ChurchTools
        :param source_filepath: file to be opened e.g. with open('media/pinguin.png', 'rb')
        :type source_filepath: str
        :param domain_type:  The ct_domain type, currently supported are 'avatar', 'groupimage', 'logo', 'attatchments',
         'html_template', 'service', 'song_arrangement', 'importtable', 'person', 'familyavatar', 'wiki_.?'.
        :type domain_type: str
        :param domain_identifier: ID of the object in ChurchTools
        :type domain_identifier: int
        :param custom_file_name: optional file name - if not specified the one from the file is used
        :type custom_file_name: str
        :param overwrite: if true delete existing file before upload of new one to replace \
        it's content instead of creating a copy
        :type overwrite: bool
        :return: if successful
        :rtype: bool
        """

        source_file = open(source_filepath, 'rb')

        url = '{}/api/files/{}/{}'.format(self.domain,
                                          domain_type, domain_identifier)

        if overwrite:
            logger.debug(
                "deleting old file {} before new upload".format(source_file))
            delete_file_name = source_file.name.split(
                '/')[-1] if custom_file_name is None else custom_file_name
            self.file_delete(domain_type, domain_identifier, delete_file_name)

        # add files as files form data with dict using 'files[]' as key and
        # (tuple of filename and fileobject)
        if custom_file_name is None:
            files = {'files[]': (source_file.name.split('/')[-1], source_file)}
        else:
            if '/' in custom_file_name:
                logger.warning(
                    '/ in file name ({}) will fail upload!'.format(custom_file_name))
                files = {}
            else:
                files = {'files[]': (custom_file_name, source_file)}

        response = self.session.post(url=url, files=files)
        source_file.close()

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
            try:
                response_content = json.loads(response.content)
                logger.debug("Upload successful {}".format(response_content))
                return True
            except BaseException:
                logger.warning(response.content.decode())
                return False
        else:
            logger.warning(response.content.decode())
            return False

    def file_delete(self, domain_type, domain_identifier,
                    filename_for_selective_delete=None):
        """
        Helper function to delete ALL attachments of any specified module of ChurchTools#
        or identifying individual file_name_ids and deleting specifc files only
        :param domain_type:  The ct_domain type, currently supported are 'avatar', 'groupimage', 'logo', 'attatchments',
         'html_template', 'service', 'song_arrangement', 'importtable', 'person', 'familyavatar', 'wiki_.?'.
        :type domain_type: str
        :param domain_identifier: ID of the object in ChurchTools
        :type domain_identifier: int
        :param filename_for_selective_delete: name of the file to be deleted - all others will be kept
        :type filename_for_selective_delete: str
        :return: if successful
        :rtype: bool
        """
        url = self.domain + \
            '/api/files/{}/{}'.format(domain_type, domain_identifier)

        if filename_for_selective_delete is not None:
            response = self.session.get(url=url)
            files = json.loads(response.content)['data']
            selective_file_ids = [
                item["id"] for item in files if item['name'] == filename_for_selective_delete]
            for current_file_id in selective_file_ids:
                url = self.domain + '/api/files/{}'.format(current_file_id)
                response = self.session.delete(url=url)

        # Delete all Files for the id online
        else:
            response = self.session.delete(url=url)

        return response.status_code == 204  # success code for delete action upload

    def file_download(self, filename, domain_type,
                      domain_identifier, target_path='./downloads'):
        """
        Retrieves the first file from ChurchTools for specific filename, domain_type and domain_identifier from churchtools
        :param filename: display name of the file as shown in ChurchTools
        :type filename: str
        :param domain_type: Currently supported are either 'avatar', 'groupimage', 'logo', 'attatchments', 'html_template', 'service', 'song_arrangement', 'importtable', 'person', 'familyavatar', 'wiki_.?'
        :type domain_type: str
        :param domain_identifier: = Id e.g. of song_arrangement - For songs this technical number can be obtained running get_songs()
        :type domain_identifier: str
        :param target_path: local path as target for the download (without filename) - will be created if not exists
        :type target_path: str
        :return: if successful
        :rtype: bool
        """
        StateOK = False
        CHECK_FOLDER = os.path.isdir(target_path)

        # If folder doesn't exist, then create it.
        if not CHECK_FOLDER:
            os.makedirs(target_path)
            print("created folder : ", target_path)

        url = '{}/api/files/{}/{}'.format(self.domain,
                                          domain_type, domain_identifier)

        response = self.session.get(url=url)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            arrangement_files = response_content['data'].copy()
            logger.debug(
                "SongArrangement-Files load successful {}".format(response_content))
            file_found = False

            for file in arrangement_files:
                filenameoriginal = str(file['name'])
                if filenameoriginal == filename:
                    file_found = True
                    break

            if file_found:
                logger.debug("Found File: {}".format(filename))
                # Build path OS independent
                fileUrl = str(file['fileUrl'])
                path_file = os.sep.join([target_path, filename])
                StateOK = self.file_download_from_url(fileUrl, path_file)
            else:
                logger.warning("File {} does not exist".format(filename))

            return StateOK
        else:
            logger.warning(
                "Something went wrong fetching SongArrangement-Files: {}".format(response.status_code))

    def file_download_from_url(self, file_url, target_path):
        """
        Retrieves file from ChurchTools for specific file_url from churchtools
        This function is used by file_download(...)
        :param file_url: Example file_url=https://lgv-oe.church.tools/?q=public/filedownload&id=631&filename=738db42141baec592aa2f523169af772fd02c1d21f5acaaf0601678962d06a00
                Pay Attention: this file-url consists of a specific / random filename which was created by churchtools
        :type file_url: str
        :param target_path: directory to drop the download into - must exist before use!
        :type target_path: str
        :return: if successful
        :rtype: bool
        """
        # NOTE the stream=True parameter below
        with self.session.get(url=file_url, stream=True) as r:
            if r.status_code == 200:
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
                logger.debug("Download of {} successful".format(file_url))
                return True
            else:
                logger.warning(
                    "Something went wrong during file_download: {}".format(
                        r.status_code))
                return False
