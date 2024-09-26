import json
import logging

from datetime import datetime
from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)

class ChurchToolsApiCalendar(ChurchToolsApiAbstract):
    """ Part definition of ChurchToolsApi which focuses on calendars

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_calendars(self) -> list[dict]:
        """
        Function to retrieve all calendar objects
        This does not include pagination yet

        Returns:
            Dict of calendars
        """
        url = self.domain + '/api/calendars'
        headers = {
            'accept': 'application/json'
        }
        params = {}

        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            return response_content['data'].copy()
        else:
            logger.warning(
                "%s Something went wrong fetching events: %s", response.status_code, response.content)

    def get_calendar_appointments(
            self, calendar_ids: list, **kwargs) -> list[dict]:
        """
        Retrieve a list of appointments

        Arguments:
            calendar_ids: list of calendar ids to be checked
                If an individual appointment id is requested using kwargs only one calendar can be specified
            kwargs: optional params to limit the results

        Keyword Arguments:
            from_ (str|datetime): with starting date in format YYYY-MM-DD - added _ to name as opposed to ct_api because of reserved keyword
            to_ (str|datetime): end date in format YYYY-MM-DD ONLY allowed with from_ - added _ to name as opposed to ct_api because of reserved keyword
            appointment_id (int): limit to one appointment only - requires calendarId keyword!

        Returns:
            list of calendar appointment / appointments
            simplified to appointments only if indidividual occurance is relevant (e.g. lookup by date)
            startDate and endDate overwritten by actual date if calculated date of series is unambiguous
            Nothing in case something is off or nothing exists
        """

        url = self.domain + '/api/calendars'
        params = {}

        if len(calendar_ids) > 1:
            url += '/appointments'
            params['calendar_ids[]'] = calendar_ids
        elif 'appointment_id' in kwargs.keys():
            url += f"/{calendar_ids[0]}/appointments/{kwargs['appointment_id']}"
        else:
            url += f"/{calendar_ids[0]}/appointments"

        headers = {
            'accept': 'application/json'
        }

        if 'from_' in kwargs.keys():
            from_ = kwargs['from_']
            if isinstance(from_, datetime):
                from_ = from_.strftime("%Y-%m-%d")
            if len(from_) == 10:
                params['from'] = from_
        if 'to_' in kwargs.keys() and 'from_' in kwargs.keys():
            to_ = kwargs['to_']
            if isinstance(to_, datetime):
                to_ = to_.strftime("%Y-%m-%d")
            if len(to_) == 10:
                params['to'] = to_
        elif 'to_' in kwargs.keys():
            logger.warning(
                'Use of to_ is only allowed together with from_')

        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers
            )

            result = [response_data] if isinstance(response_data, dict) else response_data

            if len(result) == 0:
                logger.info(
                    'There are not calendar appointments with the requested params')
                return
            # clean result
            elif 'base' in result[0].keys():
                merged_appointments = []
                for appointment in result:
                    appointment['base']['startDate'] = appointment['calculated']['startDate']
                    appointment['base']['endDate'] = appointment['calculated']['endDate']
                    merged_appointments.append(appointment['base'])
                return merged_appointments
            elif 'appointment' in result[0].keys():
                if len(result[0]['calculatedDates']) > 2:
                    logger.info('returning a series calendar appointment!')
                    return result
                else:
                    logger.debug(
                        'returning a simplified single calendar appointment with one date')
                    return [appointment['appointment']
                            for appointment in result]
            else:
                logger.warning('unexpected result')

        else:
            logger.warning(
                "%s Something went wrong fetching calendar appointments:  %s", response.status_code, response.content
            )
