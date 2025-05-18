"""module containing parts used for song handling."""

import json
import logging

import requests

# from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract  # noqa: ERA001 E501
from churchtools_api.tags import (
    ChurchToolsApiTags,  # which implements ChurchToolsApiAbstract
)

logger = logging.getLogger(__name__)


class ChurchToolsApiSongs(ChurchToolsApiTags):
    """Part definition of ChurchToolsApi which focuses on songs.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def get_songs(self, **kwargs: dict) -> list[dict]:
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

        used as song_source in arrangements.

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
        """Requesting CT metadata for mapping of song sources.

        Returns:
            a dictionary of {Index:{valuedict}}.
        """
        return self.get_event_masterdata(resultClass="songSources", returnAsDict=True)

    def lookup_song_source_as_id(
        self, longname: str | None = None, shortname: str | None = None
    ) -> int:
        """Converts a song_source text to the internal id.

        used as song_source in arrangements One of the arguments must be provided.

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
        name: str,
        songcategory_id: int,
        author: str = "",
        copyright: str = "",  # noqa: A002
        ccli: str = "",
        tonality: str = "",
        bpm: str = "",
        beat: str = "",
        should_practice: bool = False,
    ) -> int | None:
        """Method to create a new song using REST API.

        Arguments:
            name: Title of the Song (former title)
            songcategory_id: id of site specific songcategories former songcategory_id
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
            should_practice: - if should be highlighted for practice. defaults to False

        Returns:
            song_id: ChurchTools song_id of the Song created or None if not successful
        """
        url = self.domain + "/api/songs"

        data = {
            "name": name,
            "categoryId": songcategory_id,
            "author": author,
            "copyright": copyright,
            "ccli": ccli,
            "tonality": tonality,
            "bpm": bpm,
            "beat": beat,
            "shouldPractice": should_practice,
        }

        response = self.session.post(url=url, json=data)

        if response.status_code != requests.codes.created:
            logger.warning(
                "%s Creating song failed with: %s",
                response.status_code,
                response.content,
            )
            return None

        response_content = json.loads(response.content)
        new_id = int(response_content["data"]["id"])
        logger.debug("Song created successful with ID=%s", new_id)
        return new_id

    def edit_song(  # noqa: PLR0913
        self,
        song_id: int,
        *,
        songcategory_id: int | None = None,
        name: str | None = None,
        author: str | None = None,
        copyright: str | None = None,  # noqa: A002
        ccli: str | None = None,
        should_practice: str | None = None,
    ) -> dict:
        """Method to EDIT an existing song using REST API.

        Changes are only applied to fields that have values in respective param
        None is considered empty while '' is an empty text which clears existing values.

        NOTE - BPM and BEAT used in create are part of arrangement
        and not song therefore not editable in this method

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required
            name: Title of the Song
            songcategory_id: int id of site specific songcategories
                (created in CT Metadata)
            author: name of author or authors, ideally comma separated if multiple
            copyright: name of organization responsible for rights distribution
            ccli: CCLI ID see songselect.ccli.com/ - using "-" if empty on purpose
            should_practice: if should be highlighted for practice

        Returns: song after change
        """
        url = f"{self.domain}/api/songs/{song_id}"

        existing_song = self.get_songs(song_id=song_id)[0]

        data = {
            "id": song_id if song_id is not None else existing_song["name"],
            "name": name if name is not None else existing_song["name"],
            "categoryId": songcategory_id
            if songcategory_id is not None
            else existing_song["category"]["id"],
            "author": author if author is not None else existing_song["author"],
            "copyright": copyright
            if copyright is not None
            else existing_song["copyright"],
            "ccli": ccli if ccli is not None else existing_song["ccli"],
            "shouldPractice": should_practice
            if should_practice is not None
            else existing_song["shouldPractice"],
        }
        response = self.session.put(url=url, json=data)

        if response.status_code != requests.codes.ok:
            logger.warning(
                "%s Creating song failed with: %s",
                response.status_code,
                response.content,
            )
            return None

        return json.loads(response.content)["data"]

    def delete_song(self, song_id: int) -> bool:
        """Method to DELETE a song using REST API.

        Arguments:
            song_id: ChurchTools site specific song_id which should be modified
                required

        Returns:
            if successful
        """
        url = f"{self.domain}/api/songs/{song_id}"

        response = self.session.delete(url=url)
        if response.status_code != requests.codes.no_content:
            logger.warning(
                "%s Creating song failed with: %s",
                response.status_code,
                response.content,
            )
            return False

        return True

    def contains_song_tag(self, song_id: int, song_tag_name: str) -> bool:
        """Helper which checks if a specific song_tag_id is present on a song.

        Arguments:
            song_id: ChurchTools site specific song_id which should checked
            song_tag_name: name of the tag which should be checked

        Returns:
            bool if present
        """
        tags = self.get_tag(domain_type="song", domain_id=song_id, rtype="name_dict")
        return song_tag_name in tags

    def get_songs_by_tag(self, song_tag_name: str) -> list[dict]:
        """Helper which returns all songs that contain have a specific tag.

        Arguments:
            song_tag_name: name of a song tag that is used
                in respective ChurchTools instace

        Returns:
            list of songs
        """
        songs = self.get_songs()
        songs_dict = {song["id"]: song for song in songs}

        logger.info(
            "get_songs_by_tag will need to send a request per song "
            "method will make a short break after a couple of requests"
        )
        filtered_song_ids = [
            song_id
            for song_id in songs_dict
            if self.contains_song_tag(song_id=song_id, song_tag_name=song_tag_name)
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
            if arrangement["isDefault"]
        )

    def create_song_arrangement(self, song_id: int, arrangement_name: str) -> int:
        """Creates a new song arrangment.

        Use edit_song_arrangement to write additional params

        Arguments:
            song_id: id of the song which should be modified
            arrangement_name: human readable name of the arrangement to be created

        Returns:
            arrangement_id
        """
        url = f"{self.domain}/api/songs/{song_id}/arrangements"

        data = {
            "name": arrangement_name,
        }

        response = self.session.post(url=url, json=data)

        if response.status_code != requests.codes.created:
            logger.warning(
                "%s Creating song arrangement failed with: %s",
                response.status_code,
                response.content,
            )
            return None

        return json.loads(response.content)["data"]["id"]

    def edit_song_arrangement(
        self,
        song_id: int,
        arrangement_id: int,
        **kwargs: dict,
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
            key: (str) e.g. Ab.
            bpm: (str) beats per minute.
            beat: (str) e.g. 4/4.
            duration: (int) lenght in full seconds.
            note: (str) more detailed explanation text.
            source_id: (int) id of the source as defined in masterdata
            source_name_short: (str) short name of source - will be mapped to source_id
            source_name: (str) full name of source - will be mapped to source_id
            source_reference: (str) source reference e.g. number within source.

        Returns:
            if changes were applied successful
        """
        url = f"{self.domain}/api/songs/{song_id}/arrangements/{arrangement_id}"

        existing_arrangement = self.get_song_arrangement(
            song_id=song_id, arrangement_id=arrangement_id
        )
        if isinstance(kwargs.get("source_id"), int):
            source_id = kwargs.get("source_id")
        elif isinstance(kwargs.get("source_name_short"), str):
            source_id = self.lookup_song_source_as_id(
                shortname=kwargs.get("source_name_short")
            )
        elif isinstance(kwargs.get("source_name"), str):
            source_id = self.lookup_song_source_as_id(
                longname=kwargs.get("source_name")
            )
        else:
            source_id = self.lookup_song_source_as_id(
                shortname=existing_arrangement["sourceName"]
            )
        data = {
            "name": kwargs.get("name", existing_arrangement["name"]),
            "key": kwargs.get("key", existing_arrangement["key"]),
            "tempo": kwargs.get("tempo", existing_arrangement["tempo"]),
            "beat": kwargs.get("beat", existing_arrangement["bpm"]),
            "duration": kwargs.get("duration", existing_arrangement["duration"]),
            "description": kwargs.get(
                "description", existing_arrangement["description"]
            ),
            "sourceId": source_id,
            "sourceReference": kwargs.get(
                "source_reference", existing_arrangement["sourceReference"]
            ),
        }
        response = self.session.put(url=url, json=data)
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
        url = f"{self.domain}/api/songs/{song_id}/arrangements/{arrangement_id}"

        response = self.session.delete(url=url)
        if response.status_code != requests.codes.no_content:
            logger.error(response)
            return False

        return True

    def set_default_arrangement(self, song_id: int, arrangement_id: int) -> bool:
        """Modify which arrangement is labeled as default for one song.

        Args:
            song_id: the number of the song to modify
            arrangement_id: the arrangement id within the song to delete

        Returns:
            if deleted successfull
        """
        url = f"{self.domain}/api/songs/{song_id}/arrangements/{arrangement_id}/default"

        response = self.session.patch(url=url)
        if response.status_code != requests.codes.no_content:
            logger.error(response)
            return False

        return True
