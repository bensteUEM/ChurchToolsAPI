"""module containing parts used for calendar handling."""

import json
import logging
from datetime import datetime

import pytz
import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiCalendar(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on calendars.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def get_calendars(self) -> list[dict]:
        """Function to retrieve all calendar objects
        This does not include pagination yet.

        Returns:
            Dict of calendars
        """
        url = self.domain + "/api/calendars"
        headers = {"accept": "application/json"}
        params = {}

        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            return response_content["data"].copy()
        logger.warning(
            "%s Something went wrong fetching events: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_calendar_appointments(self, calendar_ids: list, **kwargs) -> list[dict]:
        """Retrieve a list of appointments.

        Arguments:
            calendar_ids: list of calendar ids to be checked
                If an individual appointment id is requested using kwargs
                only one calendar can be specified
            kwargs: optional params to limit the results

        Keyword Arguments:
            from_ (str|datetime): with starting date in format YYYY-MM-DD
                added _ to name as opposed to ct_api because of reserved keyword
            to_ (str|datetime): end date in format YYYY-MM-DD ONLY allowed with from_
                added _ to name as opposed to ct_api because of reserved keyword
            appointment_id (int): limit to one appointment only
                requires calendarId keyword!

        Returns:
            list of calendar appointment / appointments
            simplified to appointments only if indidividual occurance is relevant
                (e.g. lookup by date)
            startDate and endDate overwritten by actual date if
                calculated date of series is unambiguous
            Nothing in case something is off or nothing exists
        """
        url = self.domain + "/api/calendars"
        params = {}

        if len(calendar_ids) > 1:
            url += "/appointments"
            params["calendar_ids[]"] = calendar_ids
        elif "appointment_id" in kwargs:
            url += f"/{calendar_ids[0]}/appointments/{kwargs['appointment_id']}"
        else:
            url += f"/{calendar_ids[0]}/appointments"

        headers = {"accept": "application/json"}

        LENGTH_OF_DATE_WITH_HYPHEN = 10
        if "from_" in kwargs:
            from_ = kwargs["from_"]
            if isinstance(from_, datetime):
                from_ = from_.strftime("%Y-%m-%d")
            if len(from_) == LENGTH_OF_DATE_WITH_HYPHEN:
                params["from"] = from_
        if "to_" in kwargs and "from_" in kwargs:
            to_ = kwargs["to_"]
            if isinstance(to_, datetime):
                to_ = to_.strftime("%Y-%m-%d")
            if len(to_) == LENGTH_OF_DATE_WITH_HYPHEN:
                params["to"] = to_
        elif "to_" in kwargs:
            logger.warning("Use of to_ is only allowed together with from_")

        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )

            result = (
                [response_data] if isinstance(response_data, dict) else response_data
            )

            if len(result) == 0:
                logger.info(
                    "There are not calendar appointments with the requested params",
                )
                return None
            # clean result
            if "base" in result[0]:
                merged_appointments = []
                for appointment in result:
                    appointment["base"]["startDate"] = appointment["calculated"][
                        "startDate"
                    ]
                    appointment["base"]["endDate"] = appointment["calculated"][
                        "endDate"
                    ]
                    merged_appointments.append(appointment["base"])
                return merged_appointments
            if "appointment" in result[0]:
                if len(result[0]["calculatedDates"]) > 1:
                    logger.info("returning a series calendar appointment!")
                    return result
                logger.debug(
                    "returning a simplified single calendar appointment with one date",
                )
                return [appointment["appointment"] for appointment in result]
            logger.warning("unexpected result")
            return None

        logger.warning(
            "%s Something went wrong fetching calendar appointments:  %s",
            response.status_code,
            response.content,
        )
        return None

    def create_calender_appointment(  # noqa: PLR0913
        self,
        calendar_id: int,
        startDate: datetime,
        endDate: datetime,
        title: str,
        subtitle: str = "",
        description: str = "",
        isInternal: bool = False,  # noqa: FBT001 FBT002
        address: dict | None = None,
        link: str = "",
        **kwargs,
    ) -> dict:
        """Basic implementation of create_calendar.

        Please refer to churchtools api sample to for additional kwargs options

        Args:
            calendar_id: id of the calendar to work with
            startDate: start of the event - taking into account timezone!
            endDate: end of the event - taking into account timezone!
            title: named title
            subtitle: secondary title_. Defaults to "".
            description: more detailed description text_. Defaults to "".
            isInternal: visibility option. Defaults to False.
            address: dict containing CT relevant address information
            link: a weblink refering more details_. Defaults to "".
            kwargs: additional params as passthrough to JSON data

        Returns:
            The dict of the calendar appointment created or None
        """
        if address is None:
            address = {}

        url = self.domain + f"/api/calendars/{calendar_id}/appointments"

        headers = {"accept": "application/json"}

        data = {
            "startDate": startDate.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S")
            + "Z",
            "endDate": endDate.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            "title": title,
            "subtitle": subtitle,
            "description": description,
            "isInternal": "true" if isInternal else "false",
            "address": address,
            "link": link,
            **kwargs,
        }

        response = self.session.post(url=url, json=data, headers=headers)

        if response.status_code != requests.codes.created:
            logger.warning(json.loads(response.content).get("errors"))
            return None

        return json.loads(response.content)["data"]

    def update_calender_appointment(
        self,
        calendar_id: int,
        appointment_id: int,
        **kwargs,
    ) -> dict:
        """Method used to update calendar appointments.

        Similar to create_calender_appointment but with additional appointment_id param.
        Loads params from existing calendar_appointment
        and overwrite all provided kwargs

        See create_calendar_appointment for details about other keywords

        Args:
            calendar_id: id of the calendar to work with
            appointment_id: id of the individual calendar appointment
            kwargs: additional params as passthrough to JSON data

        Keywords:
            startDate: start of the event. Defaults to previous value if not set
            endDate: end of the event. Defaults to previous value if not set
            title: named title. Defaults to previous value if not set
            subtitle: secondary title_. Defaults to "".
            description: more detailed description text_. Defaults to "".
            isInternal: visibility option. Defaults to previous value if not set
            address: dict containing CT relevant address information
            link: a weblink refering more details_. Defaults to "".

        Returns:
            The dict of the calendar appointment updated or None in case of issues
        """
        url = (
            self.domain + f"/api/calendars/{calendar_id}/appointments/{appointment_id}"
        )

        headers = {"accept": "application/json"}

        existing_calendar_appointment = self.get_calendar_appointments(
            calendar_ids=[calendar_id], appointment_id=appointment_id
        )[0]

        # overwrite params in respective type
        for date_param in ["startDate", "endDate"]:
            if date_param in list(kwargs):
                # TODO startDate and endDate
                existing_calendar_appointment[date_param] = (
                    kwargs.pop(date_param)
                    .astimezone(pytz.utc)
                    .strftime("%Y-%m-%dT%H:%M:%S")
                    + "Z"
                )
        for bool_param in ["isInternal"]:
            if bool_param in list(kwargs):
                existing_calendar_appointment[bool_param] = (
                    "true" if kwargs.pop(bool_param) else "false"
                )
        for param in list(kwargs):
            existing_calendar_appointment[param] = kwargs.pop(param)

        # remove items that should not be updated with this function
        drop_fields = ["calendar", "@deprecated", "meta", "version"]

        updated_calendar_appointment = {
            key: value
            for key, value in existing_calendar_appointment.items()
            if value is not None and key not in drop_fields
        }

        # remove null values in address
        for address_key in list(updated_calendar_appointment.get("address", {})):
            if not updated_calendar_appointment["address"].get(address_key):
                updated_calendar_appointment["address"].pop(address_key)

        # bool cleanup
        for key in ["allDay", "isInternal"]:
            # pass
            updated_calendar_appointment[key] = (
                str(updated_calendar_appointment[key])
                if isinstance(updated_calendar_appointment[key], bool)
                else updated_calendar_appointment[key]
            )

        # submit request
        response = self.session.put(
            url=url, json=updated_calendar_appointment, headers=headers
        )

        if response.status_code != requests.codes.ok:
            logger.warning(json.loads(response.content).get("errors"))
            return None

        return json.loads(response.content)["data"]

    def delete_calender_appointment(
        self, calendar_id: int, appointment_id: int
    ) -> bool:
        """Delete a specific calendar appointment.

        Args:
            calendar_id: the calendar to modify
            appointment_id: the id of the calendar appointment

        Returns:
            if successful
        """
        url = (
            self.domain + f"/api/calendars/{calendar_id}/appointments/{appointment_id}"
        )

        headers = {"accept": "application/json"}

        response = self.session.delete(url=url, headers=headers)

        if response.status_code != requests.codes.no_content:
            logger.warning(json.loads(response.content).get("errors"))
            return False

        return True
