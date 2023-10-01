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

            if 'meta' not in response_content.keys():  # Shortcut without Pagination
                return [response_data] if isinstance(
                    response_data, dict) else response_data

            # Long part extending results with pagination
            while response_content['meta']['pagination']['current'] \
                    < response_content['meta']['pagination']['lastPage']:
                logging.info("page {} of {}".format(response_content['meta']['pagination']['current'],
                                                    response_content['meta']['pagination']['lastPage']))
                params = {
                    'page': response_content['meta']['pagination']['current'] + 1}
                response = self.session.get(
                    url=url, headers=headers, params=params)
                response_content = json.loads(response.content)
                response_data.extend(response_content['data'])

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
