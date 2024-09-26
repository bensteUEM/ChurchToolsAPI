import json
import logging
from datetime import datetime, timedelta

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract


class ChurchToolsApiSongs(ChurchToolsApiAbstract):
    """ Part definition of ChurchToolsApi which focuses on songs

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_songs(self, **kwargs) -> list[dict]:
        """Gets list of all songs from the server.

        Kwargs:
            song_id: int: optional filter by song id
        
        Returns: list of songs
        """

        url = self.domain + "/api/songs"
        if "song_id" in kwargs.keys():
            url = url + "/{}".format(kwargs["song_id"])
        headers = {"accept": "application/json"}
        params = {"limit":50} #increases default pagination size
        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers, params=params
            )
            return [response_data] if isinstance(response_data, dict) else response_data

        else:
            if "song_id" in kwargs.keys():
                logging.info(
                    "Did not find song ({}) with CODE {}".format(
                        kwargs["song_id"], response.status_code))
            else:
                logging.warning(
                    "Something went wrong fetching songs: CODE {}".format(
                        response.status_code))

    def get_song_ajax(self, song_id=None, require_update_after_seconds=10):
        """
        Legacy AJAX function to get a specific song
        used to e.g. check for tags requires requesting full song list
        for efficiency reasons songs are cached and not updated unless older than 15sec or update_required
        Be aware that params of the returned object might differ from REST API responsens (e.g. Bezeichnung instead of name)
        :param song_id: the id of the song to be searched for
        :type song_id: int
        :param require_update_after_seconds: number of seconds after which an update of ajax song cache is required
            defaults to 10 sedonds
        :type require_update_after_seconds: int
        :return: response content interpreted as json
        :rtype: dict
        """

        if self.ajax_song_last_update is None:
            require_update = True
        else:
            require_update = self.ajax_song_last_update + \
                timedelta(seconds=10) < datetime.now()
        if require_update:
            url = self.domain + '/?q=churchservice/ajax&func=getAllSongs'
            response = self.session.post(url=url)
            self.ajax_song_cache = json.loads(response.content)[
                'data']['songs']
            self.ajax_song_last_update = datetime.now()

        song = self.ajax_song_cache[str(song_id)]

        return song

    def get_song_category_map(self):
        """
        Helpfer function creating requesting CT metadata for mapping of categories
        :return: a dictionary of CategoryName:CTCategoryID
        :rtype: dict
        """

        url = self.domain + '/api/event/masterdata'
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)
        response_content = json.loads(response.content)
        song_categories = response_content['data']['songCategories']
        song_category_dict = {}
        for item in song_categories:
            song_category_dict[item['name']] = item['id']

        return song_category_dict

    def create_song(self, title: str, songcategory_id: int, author='', copyright='', ccli='', tonality='', bpm='',
                    beat=''):
        """
        Method to create a new song using legacy AJAX API
        Does not check for existing duplicates !
        function endpoint see https://api.church.tools/function-churchservice_addNewSong.html
        name for params reverse engineered based on web developer tools in Firefox and live churchTools instance

        :param title: Title of the Song
        :param songcategory_id: int id of site specific songcategories (created in CT Metadata) - required
        :param author: name of author or authors, ideally comma separated if multiple - optional
        :param copyright: name of organization responsible for rights distribution - optional
        :param ccli: CCLI ID see songselect.ccli.com/ - using "-" if empty on purpose - optional
        :param tonality: empty or specific string used for tonaly - see ChurchTools for details e.g. Ab,A,C,C# ... - optional
        :param bpm: Beats per Minute - optional
        :param beat: Beat - optional

        :return: int song_id: ChurchTools song_id of the Song created or None if not successful
        :rtype: int | None
        """
        url = self.domain + '/?q=churchservice/ajax&func=addNewSong'

        data = {
            'bezeichnung': title,
            'songcategory_id': songcategory_id,
            'author': author,
            'copyright': copyright,
            'ccli': ccli,
            'tonality': tonality,
            'bpm': bpm,
            'beat': beat
        }

        response = self.session.post(url=url, data=data)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            new_id = int(response_content['data'])
            logging.debug("Song created successful with ID={}".format(new_id))
            return new_id

        else:
            logging.info(
                "Creating song failed with {}".format(
                    response.status_code))
            return None

    def edit_song(self, song_id: int, songcategory_id=None, title=None, author=None, copyright=None, ccli=None,
                  practice_yn=None):
        """
        Method to EDIT an existing song using legacy AJAX API
        Changes are only applied to fields that have values in respective param
        None is considered empty while '' is an empty text which clears existing values

        function endpoint see https://api.church.tools/function-churchservice_editSong.html
        name for params reverse engineered based on web developer tools in Firefox and live churchTools instance
        NOTE - BPM and BEAT used in create are part of arrangement and not song therefore not editable in this method

        :param song_id: ChurchTools site specific song_id which should be modified - required

        :param title: Title of the Song
        :param songcategory_id: int id of site specific songcategories (created in CT Metadata)
        :param author: name of author or authors, ideally comma separated if multiple
        :param copyright: name of organization responsible for rights distribution
        :param ccli: CCLI ID see songselect.ccli.com/ - using "-" if empty on purpose
        :param practice_yn: bool as 0 and 1 - additional param which does not exist in create method!

        :return: response item
        :rtype: dict #TODO 49
        """

        # system/churchservice/churchservice_db.php
        url = self.domain + '/?q=churchservice/ajax&func=editSong'

        existing_song = self.get_songs(song_id=song_id)[0]

        data = {
            'id': song_id if song_id is not None else existing_song['name'],
            'bezeichnung': title if title is not None else existing_song['name'],
            'songcategory_id': songcategory_id if songcategory_id is not None else existing_song['category']['id'],
            'author': author if author is not None else existing_song['author'],
            'copyright': copyright if copyright is not None else existing_song['copyright'],
            'ccli': ccli if ccli is not None else existing_song['ccli'],
            'practice_yn': practice_yn if practice_yn is not None else existing_song['shouldPractice'],
        }

        response = self.session.post(url=url, data=data)
        return response

    def delete_song(self, song_id: int):
        """
        Method to DELETE a song using legacy AJAX API
        name for params reverse engineered based on web developer tools in Firefox and live churchTools instance

        :param song_id: ChurchTools site specific song_id which should be modified - required

        :return: response item
        :rtype: dict #TODO 49
        """

        # system/churchservice/churchservice_db.php
        url = self.domain + '/?q=churchservice/ajax&func=deleteSong'

        data = {
            'id': song_id,
        }

        response = self.session.post(url=url, data=data)
        return response

    def add_song_tag(self, song_id: int, song_tag_id: int):
        """
        Method to add a song tag using legacy AJAX API on a specific song
        reverse engineered based on web developer tools in Firefox and live churchTools instance

        re-adding existing tag does not cause any issues
        :param song_id: ChurchTools site specific song_id which should be modified - required
        :type song_id: int
        :param song_tag_id: ChurchTools site specific song_tag_id which should be added - required
        :type song_tag_id: int

        :return: response item
        :rtype: dict #TODO 49
        """
        url = self.domain + '/?q=churchservice/ajax&func=addSongTag'

        data = {
            'id': song_id,
            'tag_id': song_tag_id
        }

        response = self.session.post(url=url, data=data)
        return response

    def remove_song_tag(self, song_id, song_tag_id):
        """
        Method to remove a song tag using legacy AJAX API on a specifc song
        reverse engineered based on web developer tools in Firefox and live churchTools instance
        re-removing existing tag does not cause any issues

        :param song_id: ChurchTools site specific song_id which should be modified - required
        :type song_id: int
        :param song_tag_id: ChurchTools site specific song_tag_id which should be added - required
        :type song_tag_id: int

        :return: response item
        :rtype: dict #TODO 49
        """
        url = self.domain + '/?q=churchservice/ajax&func=delSongTag'

        data = {
            'id': song_id,
            'tag_id': song_tag_id
        }

        response = self.session.post(url=url, data=data)
        return response

    def get_song_tags(self, song_id):
        """
        Method to get a song tag workaround using legacy AJAX API for getSong
        :param song_id: ChurchTools site specific song_id which should be modified - required
        :type song_id: int
        :return: response item
        :rtype: list
        """
        song = self.get_song_ajax(song_id)
        return song['tags']

    def contains_song_tag(self, song_id, song_tag_id):
        """
        Helper which checks if a specific song_tag_id is present on a song
        :param song_id: ChurchTools site specific song_id which should checked
        :type song_id: int
        :param song_tag_id: ChurchTools site specific song_tag_id which should be searched for
        :type song_tag_id: int
        :return: bool if present
        :rtype: bool
        """
        tags = self.get_song_tags(song_id)
        return str(song_tag_id) in tags

    def get_songs_by_tag(self, song_tag_id):
        """
        Helper which returns all songs that contain have a specific tag
        :param song_tag_id: ChurchTools site specific song_tag_id which should be searched for
        :type song_tag_id: int
        :return: list of songs
        :rtype: list[dict]
        """
        songs = self.get_songs()
        songs_dict = {song['id']: song for song in songs}

        filtered_song_ids = []
        for id in songs_dict.keys():
            if self.contains_song_tag(id, song_tag_id):
                filtered_song_ids.append(id)

        result = [songs_dict[song_id] for song_id in filtered_song_ids]

        return result
