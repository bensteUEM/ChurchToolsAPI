import json
import logging

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract


class ChurchToolsApiGroups(ChurchToolsApiAbstract):
    """ Part definition of ChurchToolsApi which focuses on groups

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_groups(self, **kwargs):
        """
        Gets list of all groups
        :keyword group_id: int: optional filter by group id
        :return: dict mit allen Gruppen
        :rtype: dict
        """
        url = self.domain + '/api/groups'
        if 'group_id' in kwargs.keys():
            url = url + '/{}'.format(kwargs['group_id'])
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Groups successful {}".format(response_content))

            if 'meta' not in response_content.keys():  # Shortcut without Pagination
                return response_data

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

            return response_data
        else:
            logging.warning(
                "Something went wrong fetching groups: {}".format(
                    response.status_code))

    def get_groups_hierarchies(self):
        """
        Get list of all group hierarchies and convert them to a dict
        :return: list of all group hierarchies using groupId as key
        :rtype: dict
        """
        url = self.domain + '/api/groups/hierarchies'
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Groups Hierarchies successful {}".format(response_content))

            result = {group['groupId']: group for group in response_data}
            return result

        else:
            logging.warning(
                "Something went wrong fetching groups hierarchies: {}".format(
                    response.status_code))

    def get_group_statistics(self, group_id: int):
        """
        Get statistics for the given group
        :param group_id: required group_id
        :return: dict with statistics
        :rtype: dict
        """
        url = self.domain + '/api/groups/{}/statistics'.format(group_id)
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Group Statistics successful {}".format(response_content))
            return response_data
        else:
            logging.warning(
                "Something went wrong fetching group statistics: {}".format(
                    response.status_code))

    def create_group(self, name: str, group_status_id: int, grouptype_id: int, **kwargs):
        """
        Create a new group
        :param name: str: required name
        :param group_status_id: int: required status id
        :param grouptype_id: int: required grouptype id
        :keyword campus_id: int: optional campus id
        :keyword superior_group_id: int: optional superior group id
        :keyword force: bool: set to force create if a group with this name
                              already exists
        :return: dict with created group
        :rtype: dict
        """
        url = self.domain + '/api/groups'
        headers = {
            'accept': 'application/json'
        }
        data = {
            "groupStatusId": group_status_id,
            "groupTypeId": grouptype_id,
            "name": name,
        }

        if 'campus_id' in kwargs.keys():
            data['campusId'] = kwargs['campus_id']

        if 'force' in kwargs.keys():
            data['force'] = kwargs['force']

        if 'superior_group_id' in kwargs.keys():
            data['superiorGroupId'] = kwargs['superior_group_id']

        response = self.session.post(url=url, headers=headers, data=data)

        if response.status_code == 201:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Create Group successful {}".format(response_content))

            return response_data
        else:
            logging.warning(
                "Something went wrong with creating group: {}".format(response.status_code))

    def update_group(self, group_id: int, data: dict):
        """
        Update a field of the given group
        to loookup available names use get_group(group_id=xxx)
        :param group_id: int: required group_id
        :param data: dict: required group fields data
        :return: dict with updated group
        :rtype: dict
        """
        url = self.domain + '/api/groups/{}'.format(group_id)
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.session.patch(
            url=url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Update Group successful {}".format(response_content))

            return response_data
        else:
            logging.warning(
                "Something went wrong updating group: {}".format(
                    response.status_code))

    def delete_group(self, group_id: int):
        """
        Delete the given group
        :param group_id: int: required group_id
        :return: True if successful
        :rtype: bool
        """
        url = self.domain + '/api/groups/{}'.format(group_id)
        response = self.session.delete(url=url)

        if response.status_code == 204:
            logging.debug("First response of Delete Group successful")
            return True
        else:
            logging.warning(
                "Something went wrong deleting group: {}".format(
                    response.status_code))

    def get_grouptypes(self, **kwargs):
        """
        Get list of all grouptypes
        :keyword grouptype_id: int: optional filter by grouptype id
        :return: dict with all grouptypes with id as key (even if only one)
        :rtype: dict
        """
        url = self.domain + '/api/group/grouptypes'
        if 'grouptype_id' in kwargs.keys():
            url = url + '/{}'.format(kwargs['grouptype_id'])
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Grouptypes successful {}".format(response_content))
            if isinstance(response_data, list):
                result = {group['id']: group for group in response_data}
            else:
                result = {response_data['id']: response_data}
            return result
        else:
            logging.warning(
                "Something went wrong fetching grouptypes: {}".format(
                    response.status_code))

    def get_group_permissions(self, group_id: int):
        """
        Get permissions of the current user for the given group
        :param group_id: required group_id
        :return: dict with permissions
        :rtype: dict
        """
        url = self.domain + \
            '/api/permissions/internal/groups/{}'.format(group_id)
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Group Permissions successful {}".format(response_content))
            return response_data
        else:
            logging.warning(
                "Something went wrong fetching group permissions: {}".format(
                    response.status_code))

    def get_group_members(self, group_id: int, **kwargs):
        """
        Get list of members for the given group
        :param group_id: int: required group id
        :keyword role_ids: list[int]: optional filter list of role ids
        :return: list of group member dicts
        :rtype: list[dict]
        """
        url = self.domain + '/api/groups/{}/members'.format(group_id)
        headers = {
            'accept': 'application/json'
        }
        params = {}

        if 'role_ids' in kwargs.keys():
            params['role_ids[]'] = kwargs['role_ids']

        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug(
                "First response of Group Members successful {}".format(response_content))

            if 'meta' not in response_content.keys():  # Shortcut without Pagination
                return response_data

             # Long part extending results with pagination
            while response_content['meta']['pagination']['current'] \
                    < response_content['meta']['pagination']['lastPage']:
                logging.info("page {} of {}".format(response_content['meta']['pagination']['current'],
                                                    response_content['meta']['pagination']['lastPage']))
                params['page'] = response_content['meta']['pagination']['current'] + 1
                response = self.session.get(
                    url=url, headers=headers, params=params)
                response_content = json.loads(response.content)
                response_data.extend(response_content['data'])

            return response_data
        else:
            logging.warning(
                "Something went wrong fetching group members: {}".format(response.status_code))
