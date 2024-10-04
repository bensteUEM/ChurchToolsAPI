import json
import logging

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiResources(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on resources.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_resource_masterdata(self, result_type: str) -> dict:
        """Access to resource masterdata

        Arguments:
            result_type: either "resourceTypes" or "resources" depending on expected result

        Returns:
            dict of resource masterdata
        """
        known_result_types = ["resourceTypes", "resources"]
        if result_type not in known_result_types:
            logger.error(
                "get_resource_masterdata does not know result_type=%s", result_type
            )
            return

        url = self.domain + "/api/resource/masterdata"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers
            )

            return response_data[result_type]
        else:
            logger.error(response)
            return

    def get_bookings(self, **kwargs) -> list[dict]:
        """Access to all Resource bookings in churchtools based on a combination of Keyword Arguments.

        Arguments:
            kwargs - see list below - some combination limits do apply

        KwArgs:
            booking_id: int: only one booking by id (use standalone only)
            resources_ids:list[int]: required if not booking_id
            status_ids: list[int]: filter by list of stats ids to consider (requires resource_ids)
            _from: datetime: date range to consider (use only with _to! - might have a bug in API - Support Ticket 130123)
            _to: datetime: date range to consider (use only with _from! - might have a bug in API - Support Ticket 130123)
            appointment_id: int: get resources for one specific calendar_appointment only (use together with _to and _from for performance reasons)
        """
        url = self.domain + "/api/bookings"
        headers = {"accept": "application/json"}
        params = {"limit": 50}  # increases default pagination size

        # at least one of the following arguments is required
        required_kwargs = ["booking_id", "resource_ids"]
        if not any([kwarg in kwargs for kwarg in required_kwargs]):
            logger.error(
                "invalid argument combination in get_bookings - please check docstring for requirements"
            )
            return

        if booking_id := kwargs.get("booking_id"):
            url = url + "/{}".format(kwargs["booking_id"])
        elif resource_ids := kwargs.get("resource_ids"):
            params["resource_ids[]"] = resource_ids

            if status_ids := kwargs.get("status_ids"):
                params["status_ids[]"] = status_ids
            if "_from" in kwargs or "_to" in kwargs:
                if "_from" not in kwargs or "_to" not in kwargs:
                    logger.info(
                        "missing _from or _to defaults to first or last day of current month"
                    )
                if _from := kwargs.get("_from"):
                    params["from"] = _from.strftime("%Y-%m-%d")
                if _to := kwargs.get("_to"):
                    params["to"] = _to.strftime("%Y-%m-%d")
            if appointment_id := kwargs.get("appointment_id"):
                if "from" not in params:
                    logger.warning(
                        "using appointment ID without date range might be incomplete if current month differs"
                    )
                params["appointment_id"] = appointment_id

        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers, params=params
            )
            result_list = (
                [response_data] if isinstance(response_data, dict) else response_data
            )

            if appointment_id := kwargs.get("appointment_id"):
                return [
                    i
                    for i in result_list
                    if i["base"]["appointmentId"] == appointment_id
                ]
            else:
                return result_list
        else:
            logger.error(response.content)
            return
