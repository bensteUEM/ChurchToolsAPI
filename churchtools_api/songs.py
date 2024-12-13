from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta

import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiSongs(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on songs.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        super()

    def get_songs(self, **kwargs) -> list[dict]:
        """Gets list of all songs from the server.

        Kwargs:
            song_id: int: optional filter by song id

        Returns: list of songs
        """
        if "id" in kwargs:
            logger.warning(
                "get songs uses song_id but id was provided"
                " - are you sure you're using the correct keyword?"
            )

        url = self.domain + "/api/songs"
        if "song_id" in kwargs:
            url = url + "/{}".format(kwargs["song_id"])
        headers = {"accept": "application/json"}
        params = {"limit": 50}  # increases default pagination size
        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
                params=params,
            )
            return [response_data] if isinstance(response_data, dict) else response_data

        if "song_id" in kwargs:
            logger.info(
                "Did not find song (%s) with CODE %s",
                kwargs["song_id"],
                response.status_code,
            )
            return None
        logger.warning(
            "%s Something went wrong fetching songs: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_song_ajax(
        self, song_id: int | None = None, require_update_after_seconds: int = 10
    ) -> dict:
        """Legacy AJAX function to get a specific song.
        used to e.g. check for tags requires requesting full song list
        for efficiency reasons songs are cached and not updated
        unless older than 15sec or update_required
        Be aware that params of the returned object might differ
        from REST API responsens (e.g. Bezeichnung instead of name).

        Params:
            song_id: the id of the song to be searched for
            require_update_after_seconds: number of seconds after which
                an update of ajax song cache is required
            defaults to 10 sedonds

        Returns:
            response content interpreted as json
        """
        logging.warning(
            "Using undocumented AJAX API because "
            "function does not exist as REST endpoint"
        )
        if self.ajax_song_last_update is None:
            require_update = True
        else:
            require_update = (
                self.ajax_song_last_update
                + timedelta(seconds=require_update_after_seconds)
                < datetime.now()
            )
        if require_update:
            url = self.domain + "/?q=churchservice/ajax&func=getAllSongs"
            response = self.session.post(url=url)
            self.ajax_song_cache = json.loads(response.content)["data"]["songs"]
            self.ajax_song_last_update = datetime.now()

        return self.ajax_song_cache[str(song_id)]

    def get_song_category_map(self) -> dict:
        """Helpfer function creating requesting CT metadata for mapping of categories.

        Returns:
            a dictionary of CategoryName:CTCategoryID.
        """
        url = self.domain + "/api/event/masterdata"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)
        response_content = json.loads(response.content)
        song_categories = response_content["data"]["songCategories"]
        song_category_dict = {}
        for item in song_categories:
            song_category_dict[item["name"]] = item["id"]

        return song_category_dict

    def lookup_song_category_as_id(self, category_name: str) -> int:
        """Converts a song_category text to the internal id.
        used as song_source in arrangements

        Args:
            category_name: human readable long name of the song category

        Returns:
            id number of the song category matching the arg
        """
        song_category_mapping = self.get_song_category_map()
        result = song_category_mapping.get(category_name, None)

        if not result:
            logger.warning(
                "Can not find song category (%s) on this system", category_name
            )
            return None

        return result

    def get_song_source_map(self) -> dict:
        """Helpfer function creating requesting CT metadata for mapping of song sources.
        WARNING - uses undocumented AJAX API

        Returns:
            a dictionary of {Index:{valuedict}}.
        """
        # TODO: #124 implement using REST API once support case 135796 is resolved
        logging.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )
        url = self.domain + "/index.php?q=churchservice/ajax"
        headers = {"accept": "application/json"}
        data = {"func": "getMasterData"}
        response = self.session.post(url=url, headers=headers, data=data)
        response_content = json.loads(response.content)
        return response_content["data"]["songsource"]

    def lookup_song_source_as_id(
        self, longname: str | None = None, shortname: str | None = None
    ) -> int:
        """Converts a song_source text to the internal id.
        used as song_source in arrangements One of the arguments must be provided

        Args:
            longname: human readable long name of the source. Defaults to ""
            shortname: human readable long name of the source. Defaults to ""

        Returns:
            id number of the song_source matching the arg
        """
        if longname and shortname:
            logger.warning("too many arguments - either use shortname or longname")
            return None

        song_source_mapping = self.get_song_source_map()

        if shortname:
            return int(
                next(
                    item
                    for item in song_source_mapping.values()
                    if item["shorty"] == shortname
                )["id"]
            )
        if longname:
            return int(
                next(
                    item
                    for item in song_source_mapping.values()
                    if item["name"] == longname
                )["id"]
            )

        logger.warning("missing argument longname or shortname required")
        return None

    def create_song(  # noqa: PLR0913
        self,
        title: str,
        songcategory_id: int,
        author="",
        copyright="",  # noqa: A002
        ccli="",
        tonality="",
        bpm="",
        beat="",
    ) -> int | None:
        """Method to create a new song using legacy AJAX API
        Does not check for existing duplicates !
        function endpoint see https://api.church.tools/function-churchservice_addNewSong.html
        name for params reverse engineered based on web developer tools
        in Firefox and live churchTools instance.

        Arguments:
            title: Title of the Song
            songcategory_id: int id of site specific songcategories
                (created in CT Metadata) - required
            author: name of author or authors, ideally
                comma separated if multiple - optional
            copyright: name of organization responsible
                for rights distribution - optional
            ccli: CCLI ID see songselect.ccli.com/ - using "-"
                if empty on purpose - optional
            tonality: empty or specific string used for tonaly
                see ChurchTools for details e.g. Ab,A,C,C# ... - optional
            bpm: Beats per Minute - optional
            beat: Beat - optional

        Returns:
            song_id: ChurchTools song_id of the Song created or None if not successful
        """
        logging.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )
        url = self.domain + "/?q=churchservice/ajax&func=addNewSong"

        data = {
            "bezeichnung": title,
            "songcategory_id": songcategory_id,
            "author": author,
            "copyright": copyright,
            "ccli": ccli,
            "tonality": tonality,
            "bpm": bpm,
            "beat": beat,
        }

        response = self.session.post(url=url, data=data)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            new_id = int(response_content["data"])
            logger.debug("Song created successful with ID=%s", new_id)
            return new_id

        logger.info("Creating song failed with %s", response.status_code)
        return None

    def edit_song(  # noqa: PLR0913
        self,
        song_id: int,
        *,
        songcategory_id: int | None = None,
        title: str | None = None,
        author: str | None = None,
        copyright: str | None = None,  # noqa: A002
        ccli: str | None = None,
        practice_yn: str | None = None,
    ) -> dict:
        """Method to EDIT an existing song using legacy AJAX API
        Changes are only applied to fields that have values in respective param
        None is considered empty while '' is an empty text which clears existing values.

        function endpoint see https://api.church.tools/function-churchservice_editSong.html
        name for params reverse engineered based on web developer tools
        in Firefox and live churchTools instance
        NOTE - BPM and BEAT used in create are part of arrangement
        and not song therefore not editable in this method

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required
            title: Title of the Song
            songcategory_id: int id of site specific songcategories
                (created in CT Metadata)
            author: name of author or authors, ideally comma separated if multiple
            copyright: name of organization responsible for rights distribution
            ccli: CCLI ID see songselect.ccli.com/ - using "-" if empty on purpose
            practice_yn: bool as 0 and 1 -
                additional param which does not exist in create method!

        Returns: response item #TODO 49
        """
        # system/churchservice/churchservice_db.php
        url = self.domain + "/?q=churchservice/ajax&func=editSong"

        existing_song = self.get_songs(song_id=song_id)[0]

        data = {
            "id": song_id if song_id is not None else existing_song["name"],
            "bezeichnung": title if title is not None else existing_song["name"],
            "songcategory_id": songcategory_id
            if songcategory_id is not None
            else existing_song["category"]["id"],
            "author": author if author is not None else existing_song["author"],
            "copyright": copyright
            if copyright is not None
            else existing_song["copyright"],
            "ccli": ccli if ccli is not None else existing_song["ccli"],
            "practice_yn": practice_yn
            if practice_yn is not None
            else existing_song["shouldPractice"],
        }

        return self.session.post(url=url, data=data)

    def delete_song(self, song_id: int) -> dict:
        """Method to DELETE a song using legacy AJAX API
        name for params reverse engineered based on web developer tools
        in Firefox and live churchTools instance.

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required

        Returns:
            response item #TODO 49
        """
        logging.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )
        # system/churchservice/churchservice_db.php
        url = self.domain + "/?q=churchservice/ajax&func=deleteSong"

        data = {
            "id": song_id,
        }

        return self.session.post(url=url, data=data)

    def add_song_tag(self, song_id: int, song_tag_id: int) -> dict:
        """Method to add a song tag using legacy AJAX API on a specific song
        reverse engineered based on web developer tools in Firefox
        and live churchTools instance.

        re-adding existing tag does not cause any issues

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required
            song_tag_id: ChurchTools site specific song_tag_id which should be added
                required

        Returns:
            response item #TODO 49
        """
        logging.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )
        url = self.domain + "/?q=churchservice/ajax&func=addSongTag"

        data = {"id": song_id, "tag_id": song_tag_id}

        return self.session.post(url=url, data=data)

    def remove_song_tag(self, song_id: int, song_tag_id: int) -> dict:
        """Method to remove a song tag using legacy AJAX API on a specifc song
        reverse engineered based on web developer tools in Firefox
        and live churchTools instance
        re-removing existing tag does not cause any issues.

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required
            song_tag_id: ChurchTools site specific song_tag_id which should be added
                required

        Returns:
            response item #TODO 49
        """
        logging.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )
        url = self.domain + "/?q=churchservice/ajax&func=delSongTag"

        data = {"id": song_id, "tag_id": song_tag_id}

        return self.session.post(url=url, data=data)

    def get_song_tags(self, song_id: int, *, rtype: str = "original") -> list:
        """Method to get a song tag workaround using legacy AJAX API for getSong.

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required
            rtype: optional return type filter either original, id_dict, name_dict

        Returns:
            response item in requested format
        """
        song = self.get_song_ajax(song_id)

        match rtype:
            case "original":
                return song["tags"]
            case "id_dict":
                return {
                    tag_id: self.get_tags(type="songs", rtype="id_dict")[tag_id]
                    for tag_id in song["tags"]
                }
            case "name_dict":
                return {
                    self.get_tags(type="songs", rtype="id_dict")[tag_id]: tag_id
                    for tag_id in song["tags"]
                }

    def contains_song_tag(self, song_id: int, song_tag_id: int) -> bool:
        """Helper which checks if a specific song_tag_id is present on a song.

        Arguments:
            song_id: ChurchTools site specific song_id which should checked
            song_tag_id: ChurchTools site specific song_tag_id which should used

        Returns:
            bool if present
        """
        tags = self.get_song_tags(song_id)
        return song_tag_id in tags

    def get_songs_by_tag(self, song_tag_id) -> list[dict]:
        """Helper which returns all songs that contain have a specific tag.

        :param song_tag_id: ChurchTools site specific song_tag_id which should be used
        :type song_tag_id: int
        :return: list of songs
        """
        songs = self.get_songs()
        songs_dict = {song["id"]: song for song in songs}

        filtered_song_ids = [
            song_id
            for song_id in songs_dict
            if self.contains_song_tag(song_id=song_id, song_tag_id=song_tag_id)
        ]

        return [songs_dict[song_id] for song_id in filtered_song_ids]

    def get_song_arrangement(
        self, song_id: int, arrangement_id: int | None = None
    ) -> dict:
        """Retrieve a specific song arrangement.

        Arguments:
            song_id: number of the song - usually shown at bottom right songView in CT
            arrangement_id: id of the arrangement nested within the song
                only visible in API. Defaults to default arrangement.

        Returns:
            dict from song arrangement (from REST API)
        """
        song = self.get_songs(song_id=song_id)[0]
        if arrangement_id:
            return next(
                arrangement
                for arrangement in song["arrangements"]
                if arrangement["id"] == arrangement_id
            )

        return next(
            arrangement
            for arrangement in song["arrangements"]
            if song["arrangements"][0]["isDefault"]
        )

    def create_song_arrangement(self, song_id: int, arrangement_name: str) -> int:
        """Creates a new song arrangment.

        Arguments:
            song_id: id of the song which should be modified
            arrangement_name: human readable name of the arrangement to be created

        Returns:
            arrangement_id
        """
        logging.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )

        url = self.domain + "/?q=churchservice/ajax"

        data = {
            "func": "addArrangement",
            "song_id": song_id,
            "bezeichnung": arrangement_name,
        }
        response = self.session.post(url=url, data=data)
        if response.status_code != requests.codes.ok:
            logger.error(response)
            return None

        return json.loads(response.content)["data"]

    def edit_song_arrangement(
        self,
        song_id: int,
        arrangement_id: int,
        **kwargs,
    ) -> bool:
        """Updates a existing song arrangment.

        Overwrites param with empty default value argument if not specified!

        Args:
            song_id: song id from churchtools
            arrangement_id: arrangement id from respective song
            kwargs: optional keyword arguments as listed below
                preserves original state if not specified

        Kwargs
            name: (str) originally called "bezeichnung in CT"
            source_id: (int|str) id of the source as defined in masterdata.
                Alternatively also accepts shortname.
            source_ref: (str) source reference number.
            tonality: (str) e.g. Ab.
            bpm: (str) beats per minute.
            beat: (str) e.g. 4/4.
            length_min: (int) lenght in full minutes.
            length_sec: (int) length addiotn - seconds.
            note: (str) more detailed explanation text.

        Returns:
            if changes were applied
        """
        logger.warning(
            "Using undocumented AJAX API"
            " because function does not exist as REST endpoint"
        )
        url = self.domain + "/?q=churchservice/ajax"

        existing_arrangement = self.get_song_arrangement(
            song_id=song_id, arrangement_id=arrangement_id
        )

        if isinstance(kwargs.get("source_id"), int):
            source_id = kwargs.get("source_id")
        elif isinstance(kwargs.get("source_id"), str):
            source_id = self.lookup_song_source_as_id(shortname=kwargs.get("source_id"))
        else:
            source_id = self.lookup_song_source_as_id(
                shortname=existing_arrangement["sourceName"]
            )

        data = {
            "func": "editArrangement",
            "song_id": song_id,
            "id": arrangement_id,
            "bezeichnung": kwargs.get("name", existing_arrangement["name"]),
            "source_id": source_id,
            "source_ref": kwargs.get(
                "source_ref", existing_arrangement["sourceReference"]
            ),
            "tonality": kwargs.get(
                "tonality", existing_arrangement["keyOfArrangement"]
            ),
            "bpm": kwargs.get("bpm", existing_arrangement["bpm"]),
            "beat": kwargs.get("beat", existing_arrangement["bpm"]),
            "length_min": kwargs.get(
                "length_min", existing_arrangement["duration"] // 60
            ),
            "length_sec": kwargs.get(
                "length_sec", existing_arrangement["duration"] % 60
            ),
            "note": kwargs.get("note", existing_arrangement["note"]),
        }
        response = self.session.post(url=url, data=data)
        if response.status_code != requests.codes.ok:
            logger.error(json.loads(response.content)["errors"])
            return False

        return True

    def delete_song_arrangement(self, song_id: int, arrangement_id: int) -> bool:
        """Deletes a specific song arrangement.

        Args:
            song_id: the number of the song to modify
            arrangement_id: the arrangement id within the song to delete

        Returns:
            if deleted successfull
        """
        url = self.domain + "/?q=churchservice/ajax"

        data = {
            "func": "delArrangement",
            "song_id": song_id,
            "id": arrangement_id,
        }
        response = self.session.post(url=url, data=data)
        if response.status_code != requests.codes.ok:
            logger.error(response)
            return False

        return True
