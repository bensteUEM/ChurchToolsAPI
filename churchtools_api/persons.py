"""module containing parts used for person handling."""

import json
import logging

import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiPersons(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on persons.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def get_persons(self, **kwargs: dict) -> list[dict]:
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

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            logger.debug(
                "len of first response of GET Persons successful len=%s",
                len(response_content),
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

            logger.debug("Persons load successful len=%s", len(response_data))
            return response_data
        logger.info("Persons requested failed: %s", response.status_code)
        return None

    def get_persons_masterdata(
        self,
        *,
        resultClass: str | None = None,
        returnAsDict: bool = False,
    ) -> list | list[list] | dict | list[dict]:
        """Function to get the Masterdata of the persons module.

        This information is required to map some IDs to specific items.
        Special case treatment for resultClass sexes
            first item is copied for "None" references as fallback

        Arguments:
            resultClass: the name of the masterdata to retrieve. Defaults to All
            returnAsDict: if the list with one type should be returned as dict by ID

        Returns:
            list of masterdata items, if multiple types list of lists (by type) if.
        """
        url = self.domain + "/api/person/masterdata"

        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            if resultClass:
                response_data = response_data[resultClass]
                if resultClass == "sexes":
                    response_data.insert(0, {**response_data[0], "id": None})
                if returnAsDict:
                    response_data = {item["id"]: item["name"] for item in response_data}
                    response_data[None] = response_data[0]

            logger.debug("Person Masterdata load successful len=%s", len(response_data))

            return response_data
        logger.warning(
            "%s Something went wrong fetching person metadata: %s",
            response.status_code,
            response.content,
        )
        return None

    def create_person(self, person_data: dict) -> dict | None:
        """Function to create a person to ChurchTools.

        Arguments:
            person_data: dict with person data according to CT API
                firstName
                lastName
                email

                and additional optional fields using the following deafults:
                * departmentIds defaults to 0
                * statusId defaults to 0 (unknown)
                * campusId defaults to 0 (first campus)
                * privacyPolicyAgreementTypeId defaults to 1 (Gruppenanmeldeforumular)
                * privacyPolicyAgreementWhoId defaults to 1 (Person selbst)
                * privacyPolicyAgreementDate defaults to "1900-01-01"

        Permissions:
            create person

        Returns:
            dict with created person data including new ID
        """
        # add default keys if not provided
        required_keys = ["firstName", "lastName", "email"]
        if not all(key in person_data for key in required_keys):
            logger.error(
                "Person creation failed: missing required keys in person_data: %s",
                required_keys,
            )
            return None

        default_keys = {
            "departmentIds": [1],
            "statusId": 0,  # Unkonwn
            "campusId": 0,  # First Campus
            "email": "no-mail@nomail.xx",
            "privacyPolicyAgreementTypeId": 1,  # Gruppenanmeldeforumular
            "privacyPolicyAgreementWhoId": 1,  # Person selbst
            "privacyPolicyAgreementDate": "1900-01-01",
        }

        for key in default_keys:
            if key not in person_data:
                person_data[key] = default_keys[key]

        # prepare request

        url = self.domain + "/api/persons"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        response = self.session.post(
            url=url, headers=headers, data=json.dumps(person_data)
        )

        # use reposonse

        if response.status_code == requests.codes.created:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            logger.debug("Person creation successful id=%s", response_data.get("id"))
            return response_data
        logger.warning(
            "Person creation failed: %s %s",
            response.status_code,
            response.content,
        )
        return None

    def delete_person(self, personId: int) -> bool:
        """Function to delete a person from ChurchTools.

        Arguments:
            personId: ID of the person to delete

        Permissions:
            delete person

        Returns:
            bool indicating success
        """
        url = self.domain + f"/api/persons/{personId}"

        headers = {
            "accept": "application/json",
        }
        response = self.session.delete(url=url, headers=headers)

        if response.status_code == requests.codes.no_content:
            logger.debug("Person deletion successful id=%s", personId)
            return True
        logger.warning(
            "Person deletion failed id=%s: %s %s",
            personId,
            response.status_code,
            response.content,
        )
        return False
