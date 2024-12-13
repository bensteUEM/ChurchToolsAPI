import json
import logging

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiPersons(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on persons.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        super()

    def get_persons(self, **kwargs) -> list[dict]:
        """Function to get list of all or a person from CT.

        Arguments:
            kwargs: optional keywords as listed

        Kwargs:
            ids: list: of a ids filter
            returnAsDict: bool: true if should return a dict instead of list

        Permissions:
            some fields e.g. sexId require "security level person" with at least
            level 2 (administer persons is not sufficient)

        Returns:
            list of user dicts
        """
        url = self.domain + "/api/persons"
        params = {"limit": 50}  # increases default pagination size
        if "ids" in kwargs:
            params["ids[]"] = kwargs["ids"]

        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            logger.debug(
                "len of first response of GET Persons successful len(%s)",
                response_content,
            )

            if len(response_data) == 0:
                logger.warning(
                    "Requesting ct_users %s returned an empty response - "
                    "make sure the user has correct permissions",
                    params,
                )

            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
                params=params,
            )
            response_data = (
                [response_data] if isinstance(response_data, dict) else response_data
            )

            if kwargs.get("returnAsDict") and "serviceId" not in kwargs:
                result = {}
                for item in response_data:
                    result[item["id"]] = item
                response_data = result

            logger.debug("Persons load successful %s", response_data)
            return response_data
        logger.info("Persons requested failed: %s", response.status_code)
        return None

    def get_persons_masterdata(
        self,
        *,
        resultClass: str | None = None,
        returnAsDict: bool = False,
    ) -> list | list[list] | dict | list[dict]:
        """Function to get the Masterdata of the persons module
        This information is required to map some IDs to specific items.

        Arguments:
            resultClass: the name of the masterdata to retrieve. Defaults to All
            returnAsDict: if the list with one type should be returned as dict by ID

        Returns:
            list of masterdata items, if multiple types list of lists (by type) if.
        """
        url = self.domain + "/api/person/masterdata"

        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            if resultClass:
                response_data = response_data[resultClass]
                if returnAsDict:
                    response_data = {item["id"]: item["name"] for item in response_data}

            logger.debug("Person Masterdata load successful len=%s", response_data)

            return response_data
        logger.warning(
            "%s Something went wrong fetching person metadata: %s",
            response.status_code,
            response.content,
        )
        return None
