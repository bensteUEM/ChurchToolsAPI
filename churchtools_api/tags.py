"""module containing parts used for tag handling."""

import json
import logging

import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiTags(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on tags.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def create_tag(self, name: str, tag_type: str) -> bool:
        """Create a new tag.

        Args:
            name: name of the tag
            tag_type: category of the tag - at present "persons" and "songs" supported

        Returns:
            if successful
        """
        # TODO @benste: consider implementing groups too
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/92
        url = self.domain + "/api/tags"
        headers = {"accept": "application/json"}
        data = {"name": name, "type": tag_type}
        response = self.session.post(url=url, headers=headers, json=data)

        response_content = json.loads(response.content)

        if response.status_code != requests.codes.ok:
            logger.warning(response_content["errors"])
            return False

        response_content = json.loads(response.content)
        return True

    def delete_tag(self, name: str, tag_type: str) -> bool:
        """Placeholder for tag delete as soon as CT does support it.

        Args:
            name: name of the tag
            tag_type: category of the tag - at present "persons" and "songs" supported

        Returns:
            if successful
        """
        # TODO @benste: consider implementing groups too - CT Support
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/92
        logger.exception("Function does not exist in CT API yet")
        # TODO @benste: not tested because of CT Support issue 136613
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/92
        url = self.domain + "/api/tags"
        headers = {"accept": "application/json"}
        data = {"name": name, "type": tag_type}
        response = self.session.delete(url=url, headers=headers, json=data)

        response_content = json.loads(response.content)

        if response.status_code != requests.codes.no_content:
            logger.warning(response_content["errors"])
            return False

        return True

    def get_tags(self, type: str = "songs", rtype: str = "original") -> list[dict]:  # noqa: A002
        # TODO @benste: rename type to tag_type
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/127
        # TODO @benste: consider implementing groups too
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/92
        """Retrieve a list of all available tags of a specific ct_domain type from CT.

        Purpose: be able to find out tag-ids of all available tags for filtering by tag.

        Arguments:
            type: 'songs' (default) or 'persons'
            rtype: original, id_dict or name_dict.
                Defaults to original only available if combined with type


        Returns:
            list of dicts describing each tag. Each contains keys 'id' and 'name'
        """
        url = self.domain + "/api/tags"
        headers = {"accept": "application/json"}
        params = {
            "type": type,
        }
        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code != requests.codes.ok:
            logger.warning(
                "%s Something went wrong fetching Song-tags: %s",
                response.status_code,
                response.content,
            )
            return None

        response_content = json.loads(response.content)
        response_content["data"].copy()
        logger.debug("SongTags load successful %s", response_content)

        response_data = response_content["data"]

        if type:
            match rtype:
                case "id_dict":
                    return {item["id"]: item["name"] for item in response_data}
                case "name_dict":
                    return {item["name"]: item["id"] for item in response_data}
                case _:
                    return response_data

        logger.debug("SongTags load successful %s", response_content)
        return response_data
