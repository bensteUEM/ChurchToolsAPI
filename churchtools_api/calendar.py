import json
import logging

from datetime import datetime
from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract


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
            logging.warning(
                "Something went wrong fetching events: %s", response.status_code)

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
            logging.warning(
                'Use of to_ is only allowed together with from_')

        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of calendar appointments successful %s", response_content)

            if 'meta' not in response_content.keys():  # Shortcut without Pagination
                result = [response_data] if isinstance(
                    response_data, dict) else response_data

            elif 'pagination' not in response_content['meta'].keys():
                result = [response_data] if isinstance(
                    response_data, dict) else response_data

                # Long part extending results with pagination
                # TODO #1 copied from other method unsure if pagination works the
                # same as with groups
            else:
                while response_content['meta']['pagination']['current'] \
                        < response_content['meta']['pagination']['lastPage']:
                    logging.info("page %s of %s",
                                 response_content['meta']['pagination']['current'],
                                 response_content['meta']['pagination']['lastPage'])
                    params = {
                        'page': response_content['meta']['pagination']['current'] + 1}
                    response = self.session.get(
                        url=url, headers=headers, params=params)
                    response_content = json.loads(response.content)
                    response_data.extend(response_content['data'])
                result = response_data

            # clean result
            if 'base' in result[0].keys():
                merged_appointments = []
                for appointment in result:
                    appointment['base']['startDate'] = appointment['calculated']['startDate']
                    appointment['base']['endDate'] = appointment['calculated']['endDate']
                    merged_appointments.append(appointment['base'])
                return merged_appointments
            elif 'appointment' in result[0].keys():
                if len(result[0]['calculatedDates']) > 2:
                    logging.info('returning a series calendar appointment!')
                    return result
                else:
                    logging.debug(
                        'returning a simplified single calendar appointment with one date')
                    return [appointment['appointment']
                            for appointment in result]
            else:
                logging.warning('unexpected result')

        else:
            logging.warning(
                "Something went wrong fetching calendar appointments: %s",
                response.status_code)
