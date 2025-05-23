"""module containing parts used for resource handling."""

import json
import logging

import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiResources(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on resources.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def get_resource_masterdata(
        self, *, resultClass: str | None = None, returnAsDict: bool = False
    ) -> dict:
        """Access to resource masterdata.

        Arguments:
            resultClass: the key from CT resource masterdata to use. Defaults. to all,
            returnAsDict: modified resultClass to {id:name, ...}  = False,

        Returns:
            dict of resource masterdata
        """
        known_result_types = ["resourceTypes", "resources"]
        if resultClass and resultClass not in known_result_types:
            logger.error(
                "get_resource_masterdata does not know result_type=%s",
                resultClass,
            )
            return None

        url = self.domain + "/api/resource/masterdata"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )

            if resultClass:
                response_data = response_data[resultClass]
                if returnAsDict:
                    response_data = {item["id"]: item for item in response_data}
            return response_data
        logger.error(response)
        return None

    def get_bookings(self, **kwargs: dict) -> list[dict]:
        """Access to all Resource bookings in churchtools.

        based on a combination of Keyword Arguments.

        Arguments:
            kwargs: see list below - some combination limits do apply

        Keywords:
            booking_id: int: only one booking by id (use standalone only)
            resource_ids:list[int]: required if not booking_id
            status_ids: list[int]: filter by list of stats ids
                to consider (requires resource_ids)
            from_: datetime: date range to consider (use only with to_! -
                might have a bug in API - Support Ticket 130123)
            to_: datetime: date range to consider (use only with from_! -
                might have a bug in API - Support Ticket 130123)
            appointment_id: int: get resources for one specific calendar_appointment
                only (use together with to_ and from_ for performance reasons)
        """
        url = self.domain + "/api/bookings"
        headers = {"accept": "application/json"}
        params = {"limit": 50}  # increases default pagination size

        # at least one of the following arguments is required
        required_kwargs = ["booking_id", "resource_ids"]
        if not any(kwarg in kwargs for kwarg in required_kwargs):
            logger.error(
                "invalid argument combination in get_bookings"
                " - please check docstring for requirements",
            )
            return None

        if booking_id := kwargs.get("booking_id"):
            url = url + f"/{booking_id}"
        elif kwargs.get("resource_ids"):
            params = self._get_bookings_params(params=params, **kwargs)

        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code != requests.codes.ok:
            logger.error(response.content)
            return None
        response_content = json.loads(response.content)

        response_data = self.combine_paginated_response_data(
            response_content,
            url=url,
            headers=headers,
            params=params,
        )
        result_list = (
            [response_data] if isinstance(response_data, dict) else response_data
        )

        if appointment_id := kwargs.get("appointment_id"):
            return [
                i for i in result_list if i["base"]["appointmentId"] == appointment_id
            ]
        return result_list

    def _get_bookings_params(self, params: dict, **kwargs: dict) -> dict:
        """Helper function for get bookings that prepares params.

        Arguments:
            params: existing params which were set before
            kwargs: additional kwargs which should be transformed into params

        Returns:
            params dict which can be used for request
        """
        params["resource_ids[]"] = kwargs.get("resource_ids")

        if status_ids := kwargs.get("status_ids"):
            params["status_ids[]"] = status_ids
        if "from_" in kwargs or "to_" in kwargs:
            if "from_" not in kwargs or "to_" not in kwargs:
                logger.info(
                    "missing from_ or to_ defaults"
                    " to first or last day of current month",
                )
            if from_ := kwargs.get("from_"):
                params["from"] = from_.strftime("%Y-%m-%d")
            if to_ := kwargs.get("to_"):
                params["to"] = to_.strftime("%Y-%m-%d")
        if appointment_id := kwargs.get("appointment_id"):
            if "from" not in params:
                logger.warning(
                    "using appointment ID without date range"
                    " might be incomplete if current month differs",
                )
            params["appointment_id"] = appointment_id

        return params
