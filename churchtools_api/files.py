"""module containing parts used for file handling."""

import json
import logging
from pathlib import Path

import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiFiles(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on files.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def file_upload(
        self,
        source_filepath: str,
        domain_type: str,
        domain_identifier: int,
        custom_file_name: str | None = None,
        *,
        overwrite: bool = False,
    ) -> bool:
        """Helper function to upload an attachment to any module of ChurchTools.

        Params:
            source_filepath: file to be opened e.g. with open('media/pinguin.png', 'rb')
            domain_type:  The ct_domain type, currently supported are
                'avatar', 'groupimage', 'logo', 'attatchments',
                'html_template', 'service', 'song_arrangement',
                'importtable', 'person', 'familyavatar', 'wiki_.?'.
            domain_identifier: ID of the object in ChurchTools
            custom_file_name: optional file name -
                if not specified the one from the file is used
        :type custom_file_name:
            overwrite: if true delete existing file before upload of new one to replace
            it's content instead of creating a copy

        Returns:
            if successful.
        """
        source_filepath = Path(source_filepath)
        with source_filepath.open("rb") as source_file:
            url = f"{self.domain}/api/files/{domain_type}/{domain_identifier}"

            if overwrite:
                logger.debug("deleting old file %s before new upload", source_file)
                delete_file_name = (
                    source_file.name.split("/")[-1]
                    if custom_file_name is None
                    else custom_file_name
                )
                self.file_delete(domain_type, domain_identifier, delete_file_name)

            # add files as files form data with dict using 'files[]' as key and
            # (tuple of filename and fileobject)
            if custom_file_name is None:
                files = {"files[]": (source_file.name.split("/")[-1], source_file)}
            elif "/" in custom_file_name:
                logger.warning(
                    "/ in file name (%s) will fail upload!", custom_file_name
                )
                files = {}
            else:
                files = {"files[]": (custom_file_name, source_file)}

            response = self.session.post(url=url, files=files)

        """
        # Issues with HEADERS in Request module when using non standard 'files[]'
        # key in POST Request
        # Workaround for ChurchTools - generate session with /api/whoami
        # GET request and reuse it
        # Requests module usually automatically completes required header
        # Params e.g. Content-Type ...
        # in case manual header e.g. for AUTH is used, headers don't auto complete
        # and server rejects messsages or data is ommited
        # Error Code 500 is also missing in API documentation

        headers = {'Authorization': 'Login GEHEIM'}
        response_test = requests.post(url=url, headers=headers, files=files)
        #> this fails !
        """

        if response.status_code == requests.codes.ok:
            try:
                response_content = json.loads(response.content)
                logger.debug("Upload successful len=%s", response_content)
            except (json.JSONDecodeError, TypeError, UnicodeDecodeError):
                logger.warning(response.content.decode())
                return False
            else:
                return True
        else:
            logger.warning(response.content.decode())
            return False

    def file_delete(
        self,
        domain_type: str,
        domain_identifier: int,
        filename_for_selective_delete: str | None = None,
    ) -> bool:
        """Helper function to delete ALL attachments
            of any specified module of ChurchTools#
        or identifying individual file_name_ids and deleting specifc files only.

        Params:
            domain_type:  The ct_domain type, currently supported are
                'avatar', 'groupimage', 'logo', 'attatchments',
                'html_template', 'service', 'song_arrangement',
                'importtable', 'person', 'familyavatar', 'wiki_.?'.
            domain_identifier: ID of the object in ChurchTools
            filename_for_selective_delete: name of the file to be deleted -
                all others will be kept

        Returns:
            if successful.
        """
        url = self.domain + f"/api/files/{domain_type}/{domain_identifier}"

        if filename_for_selective_delete is not None:
            response = self.session.get(url=url)
            files = json.loads(response.content)["data"]
            selective_file_ids = [
                item["id"]
                for item in files
                if item["name"] == filename_for_selective_delete
            ]
            for current_file_id in selective_file_ids:
                url = self.domain + f"/api/files/{current_file_id}"
                response = self.session.delete(url=url)

        # Delete all Files for the id online
        else:
            response = self.session.delete(url=url)

        return response.status_code == requests.codes.no_content
        # success code for delete action upload

    def file_download(
        self,
        filename: str,
        domain_type: str,
        domain_identifier: str,
        target_path: str = "./downloads",
    ) -> bool:
        """Retrieves the first file from ChurchTools for specific filename,
            domain_type and domain_identifier from churchtools.

        Params:
            filename: display name of the file as shown in ChurchTools
            domain_type:  The ct_domain type, currently supported are
                'avatar', 'groupimage', 'logo', 'attatchments',
                'html_template', 'service', 'song_arrangement',
                'importtable', 'person', 'familyavatar', 'wiki_.?'.
            domain_identifier: = Id e.g. of song_arrangement -
                For songs this technical number can be obtained running get_songs()
            target_path: local path as target for the download (without filename) -
                will be created if not exists

        Returns:
            if successful.
        """
        StateOK = False

        target_path = Path(target_path)
        target_path.mkdir(parents=True, exist_ok=True)

        url = f"{self.domain}/api/files/{domain_type}/{domain_identifier}"

        response = self.session.get(url=url)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            arrangement_files = response_content["data"].copy()
            logger.debug(
                "SongArrangement-Files load successful len=%s",
                response_content,
            )
            file_found = False

            for file in arrangement_files:
                filenameoriginal = str(file["name"])
                if filenameoriginal == filename:
                    file_found = True
                    break

            if file_found:
                logger.debug("Found File: %s", filename)
                # Build path OS independent
                fileUrl = str(file["fileUrl"])
                path_file = target_path / filename
                StateOK = self.file_download_from_url(fileUrl, path_file)
            else:
                logger.warning("File %s does not exist", filename)

            return StateOK
        logger.warning(
            "%s Something went wrong fetching SongArrangement-Files: %s",
            response.status_code,
            response.content,
        )
        return None

    def file_download_from_url(self, file_url: str, target_path: str) -> bool:
        """Retrieves file from ChurchTools for specific file_url from churchtools.
        This function is used by file_download(...).

        Params:
            file_url: Example file_url=https://lgv-oe.church.tools/?q=public/filedownload&id=631&filename=738db42141baec592aa2f523169af772fd02c1d21f5acaaf0601678962d06a00
                Pay Attention: this file-url consists of a specific / random
                filename which was created by churchtools
            target_path: directory to drop the download into - must exist before use!

        Returns:
            if successful.
        """
        # NOTE the stream=True parameter below

        target_path = Path(target_path)
        with self.session.get(url=file_url, stream=True) as response:
            if response.status_code == requests.codes.ok:
                with target_path.open("wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        # If you have chunk encoded response uncomment if
                        # and set chunk_size parameter to None.
                        # if chunk:
                        f.write(chunk)
                logger.debug("Download of %s successful", file_url)
                return True
            logger.warning(
                "%s Something went wrong during file_download: %s",
                response.status_code,
                response.content,
            )
            return False
