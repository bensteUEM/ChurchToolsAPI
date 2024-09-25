import json
import logging

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract


class ChurchToolsApiPersons(ChurchToolsApiAbstract):
    """ Part definition of ChurchToolsApi which focuses on persons

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_persons(self, **kwargs):
        """
        Function to get list of all or a person from CT
        :param kwargs: optional keywords as listed
        :keyword ids: list: of a ids filter
        :keyword returnAsDict: bool: true if should return a dict instead of list
        :return: list of user dicts
        :rtype: list[dict]
        """
        url = self.domain + '/api/persons'
        params = {}
        if 'ids' in kwargs.keys():
            params['ids[]'] = kwargs['ids']

        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, params=params, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()

            logging.debug(
                "First response of GET Persons successful {}".format(response_content))

            if len(response_data) == 0:
                logging.warning('Requesting ct_users {} returned an empty response - '
                                'make sure the user has correct permissions'.format(params))

            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers
            )
            response_data = [response_data] if isinstance(response_data, dict) else response_data

            if 'returnAsDict' in kwargs and not 'serviceId' in kwargs:
                if kwargs['returnAsDict']:
                    result = {}
                    for item in response_data:
                        result[item['id']] = item
                    response_data = result

            logging.debug("Persons load successful {}".format(response_data))
            return response_data
        else:
            logging.info(
                "Persons requested failed: {}".format(
                    response.status_code))
            return None
