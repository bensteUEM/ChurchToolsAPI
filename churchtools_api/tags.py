"""module containing parts used for song handling."""

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

    def get_tags(self, domain_type: str, *, rtype: str = "original") -> list[dict]:
        """Retrieve a list of all available tags.

        of a specific ct_domain type from ChurchTools
        Purpose: be able to find out tag-ids of all available tags for filtering by tag.

        Arguments:
            domain_type: 'song', 'person', 'group'
            rtype: original, id_dict or name_dict.
                Defaults to original
        Returns:
            list of dicts usually with one dict per tag with
        """
        url = f"{self.domain}/api/tags/{domain_type}"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        response_content = json.loads(response.content)

        if response.status_code != requests.codes.ok:
            logger.warning(response.content)
            return None

        response_data = response_content["data"]

        match rtype:
            case "id_dict":
                result = {item["id"]: item["name"] for item in response_data}
            case "name_dict":
                result = {item["name"]: item["id"] for item in response_data}
            case _:
                result = response_data

        logger.debug("Tag load successful len=%s", len(result))

        return result

    def add_tag(self, domain_type: str, domain_id: str, tag_name: str) -> bool:
        """Adds link to a tag to a single object.

        If Tag doesn't exist it will be created.
        If already assigned nothing will break

        Args:
            domain_type: 'song', 'person' or 'group'
            domain_id: identifier used by the object which should be modified
            tag_name: human readable name of the tag to be written

        Returns:
            if successful
        """
        url = f"{self.domain}/api/tags/{domain_type}/{domain_id}"
        headers = {"accept": "application/json"}

        params = {"name": tag_name}

        response = self.session.post(url=url, headers=headers, json=params)

        response_content = json.loads(response.content)
        if response.status_code != requests.codes.created:
            logger.warning(response_content["translatedMessage"])
            return False

        return True

    def remove_tag(self, domain_type: str, domain_id: str, tag_name: str) -> bool:
        """Removes tag from single object.

        Tags are only fully removed from the system once all allocations are removed

        Args:
            domain_type: 'song', 'person' or 'group'
            domain_id: identifier used by the object which should be modified
            tag_name: human readable name of the tag to be written

        Returns:
            if successful
        """
        tag_name_to_id = self.get_tags(domain_type=domain_type, rtype="name_dict")

        url = (
            f"{self.domain}/api/tags/"
            f"{domain_type}/{domain_id}/{tag_name_to_id[tag_name]}"
        )

        response = self.session.delete(url=url)

        if response.status_code != requests.codes.no_content:
            logger.warning(response.content)
            return False

        return True

    def get_tag(
        self, domain_type: str, domain_id: int, rtype: str = "original"
    ) -> list[dict] | None:
        """Retrieves the readable tags of one single object.

        Args:
            domain_type: 'song', 'person' or 'group'
            domain_id: identifier used by the object which should be modified
            rtype: original, id_dict or name_dict.
                Defaults to original

        Returns:
            list of tag information dicts like
                {
                    "color": "accent",
                    "description": "string",
                    "id": 0,
                    "name": "string"
                }
        """
        url = f"{self.domain}/api/tags/{domain_type}/{domain_id}"

        response = self.session.get(url=url)

        response_content = json.loads(response.content)
        if response.status_code != requests.codes.ok:
            logger.warning(response_content["translatedMessage"])
            return None

        response_data = response_content["data"]
        match rtype:
            case "id_dict":
                return {tag["id"]: tag for tag in response_data}
            case "name_dict":
                return {tag["name"]: tag for tag in response_data}
            case _:
                return response_data
