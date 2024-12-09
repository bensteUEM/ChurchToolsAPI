import json
import logging
from typing import Optional

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class ChurchToolsApiGroups(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on groups.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        super()

    def get_groups(self, **kwargs) -> list[dict]:
        """Gets list of all groups.

        Keywords:
            group_id: int: optional filter by group id (only to be used on it's own)
            kwargs: keyword arguments passthrough

        Keywords:
            group_id

        Permissions:
            requires "view group" for all groups which should be considered

        Returns:
            list of groups - either all or filtered by keyword

        """
        url = self.domain + "/api/groups"
        if "group_id" in kwargs:
            url = url + "/{}".format(kwargs["group_id"])

        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )
            return [response_data] if isinstance(response_data, dict) else response_data
        logger.warning(
            "%s Something went wrong fetching groups: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_groups_hierarchies(self):
        """Get list of all group hierarchies and convert them to a dict
        :return: list of all group hierarchies using groupId as key
        :rtype: dict.
        """
        url = self.domain + "/api/groups/hierarchies"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)
        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()
            logger.debug(
                "First response of Groups Hierarchies successful %s",
                response_content,
            )

            return {group["groupId"]: group for group in response_data}

        logger.warning(
            "%s Something went wrong fetching groups hierarchies: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_group_statistics(self, group_id: int) -> dict:
        """Get statistics for the given group.

        Args:
            group_id: required group_id

        Returns:
            statistics
        """
        url = self.domain + f"/api/groups/{group_id}/statistics"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )
            logger.debug(
                "First response of Group Statistics successful len=%s",
                response_content,
            )
            return response_data
        logger.warning(
            "%s Something went wrong fetching group statistics: %s",
            response.status_code,
            response.content,
        )
        return None

    def create_group(
        self,
        name: str,
        group_status_id: int,
        grouptype_id: int,
        **kwargs,
    ) -> dict:
        """Create a new group.

        Args:
            name: required name
            group_status_id: required status id
            grouptype_id: required grouptype id
            kwargs: keywords see below

        Kwargs:
            campus_id: int: optional campus id
            superior_group_id: int: optional superior group id
            force: bool: set to force create if a group with this name already exists

        Required Permissions:
            administer groups
            create group of grouptype

        Returns:
            dict with created group group - similar to get_group
        """
        url = self.domain + "/api/groups"
        headers = {"accept": "application/json"}
        data = {
            "groupStatusId": group_status_id,
            "groupTypeId": grouptype_id,
            "name": name,
        }

        if "campus_id" in kwargs:
            data["campusId"] = kwargs["campus_id"]

        if "force" in kwargs:
            data["force"] = kwargs["force"]

        if "superior_group_id" in kwargs:
            data["superiorGroupId"] = kwargs["superior_group_id"]

        response = self.session.post(url=url, headers=headers, data=data)

        if response.status_code == 201:
            response_content = json.loads(response.content)
            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )
            logger.debug(
                "First response of Create Group successful len=%s",
                response_content,
            )

            return response_data
        logger.warning(
            "%s Something went wrong with creating group: %s",
            response.status_code,
            response.content,
        )
        return None

    def update_group(self, group_id: int, data: dict) -> dict:
        """Update a field of the given group.
        to loookup available names use get_group(group_id=xxx).

        Arguments:
            group_id: number of the group to update
            data: all group fields

        Returns:
            dict with updated group
        """
        url = self.domain + f"/api/groups/{group_id}"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = self.session.patch(url=url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()
            logger.debug(
                "First response of Update Group successful len=%s",
                response_content,
            )

            return response_data
        logger.warning(
            "%s Something went wrong updating group: %s",
            response.status_code,
            response.content,
        )
        return None

    def delete_group(self, group_id: int) -> bool:
        """Delete the given group.

        Arguments:
            group_id: group_id

        Required Permissions
            delete group

        Returns:
            True if successful
        """
        url = self.domain + f"/api/groups/{group_id}"
        response = self.session.delete(url=url)

        if response.status_code == 204:
            logger.debug("First response of Delete Group successful")
            return True
        logger.warning(
            "%s Something went wrong deleting group: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_grouptypes(self, **kwargs):
        """Get list of all grouptypes
        :keyword grouptype_id: int: optional filter by grouptype id
        :return: dict with all grouptypes with id as key (even if only one)
        :rtype: dict.
        """
        url = self.domain + "/api/group/grouptypes"
        if "grouptype_id" in kwargs:
            url = url + "/{}".format(kwargs["grouptype_id"])
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()
            logger.debug(
                "First response of Grouptypes successful len=%s",
                response_content,
            )
            if isinstance(response_data, list):
                result = {group["id"]: group for group in response_data}
            else:
                result = {response_data["id"]: response_data}
            return result
        logger.warning(
            "%s Something went wrong fetching grouptypes: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_group_permissions(self, group_id: int):
        """Get permissions of the current user for the given group
        :param group_id: required group_id
        :return: dict with permissions
        :rtype: dict.
        """
        url = self.domain + f"/api/permissions/internal/groups/{group_id}"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()
            logger.debug(
                "First response of Group Permissions successful len=%s",
                response_content,
            )
            return response_data
        logger.warning(
            "%s Something went wrong fetching group permissions: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_group_members(self, group_id: int, **kwargs) -> list[dict]:
        """Get list of members for the given group.

        Arguments:
            group_id: group id
            kwargs: see below

        Kwargs:
            role_ids: list[int]: optional filter list of role ids

        Returns:
            list of group member dicts
        """
        url = self.domain + f"/api/groups/{group_id}/members"
        headers = {"accept": "application/json"}
        params = {}

        if "role_ids" in kwargs:
            params["role_ids[]"] = kwargs["role_ids"]

        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )
            return [response_data] if isinstance(response_data, dict) else response_data

        logger.warning(
            "%s Something went wrong fetching group members: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_groups_members(
        self,
        group_ids: Optional[list[int]] = None,
        *,
        with_deleted: bool = False,
        **kwargs,
    ) -> list[dict]:
        """Access to /groups/members to lookup group memberships
        Similar to get_group_members but not specific to a single group.

        Args:
            group_ids: list of group ids to look for. Defaults to Any
            with_deleted: If true return also delted group members. Defaults to True
            kwargs: see below

        Keywords:
            grouptype_role_ids: list[int] of grouptype_role_ids to consider
            person_ids: list[int]: person to consider for result

        Permissions:
            requires "administer persons"

        Returns:
            list of person to group assignments
        """
        url = self.domain + "/api/groups/members"
        headers = {"accept": "application/json"}
        params = {"ids[]": group_ids, with_deleted: with_deleted}

        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
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
            if grouptype_role_ids := kwargs.get("grouptype_role_ids"):
                result_list = [
                    group
                    for group in result_list
                    if group["groupTypeRoleId"] in grouptype_role_ids
                ]
            if person_ids := kwargs.get("person_ids"):
                result_list = [
                    group for group in result_list if group["personId"] in person_ids
                ]

            return result_list

            return result_list
        logger.warning(
            "%s Something went wrong fetching group members: %s",
            response.status_code,
            response.content,
        )
        return None

    def add_group_member(self, group_id: int, person_id: int, **kwargs) -> dict:
        """Add a member to a group.

        Arguments:
            group_id: required group id
            person_id: required person id
            kwargs: see below

        Keywords:
            grouptype_role_id: int: optional grouptype role id
            group_member_status: str: optional member status

        Returns:
            dict with group member
        """
        url = self.domain + f"/api/groups/{group_id}/members/{person_id}"
        headers = {
            "accept": "application/json",
        }

        data = {}
        if "grouptype_role_id" in kwargs:
            data["groupTypeRoleId"] = kwargs["grouptype_role_id"]
        if "group_member_status" in kwargs:
            data["group_member_status"] = kwargs["group_member_status"]

        response = self.session.put(url=url, data=data, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            # For unknown reasons the endpoint returns a list of items instead
            # of a single item as specified in the API documentation.
            return response_content["data"][0].copy()

        logger.warning(
            "%s Something went wrong adding group member: %s",
            response.status_code,
            response.content,
        )
        return None

    def remove_group_member(self, group_id: int, person_id: int) -> bool:
        """Remove the given group member.

        Arguments:
            group_id: int: required group id
            person_id: int: required person id

        Required Permissions:
            edit group memberships of groups
        Returns:
            True if successful
        """
        url = self.domain + f"/api/groups/{group_id}/members/{person_id}"
        response = self.session.delete(url=url)

        if response.status_code == 204:
            return True
        logger.warning(
            "%s Something went wrong removing group member: %s",
            response.status_code,
            response.content,
        )
        return None

    def get_group_roles(self, group_id: int) -> list[dict]:
        """Get list of all roles for the given group.

        Arguments:
            group_id: int: required group id
        Returns:
            list with group roles dicts
        """
        url = self.domain + f"/api/groups/{group_id}/roles"
        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)

            response_data = self.combine_paginated_response_data(
                response_content,
                url=url,
                headers=headers,
            )
            return [response_data] if isinstance(response_data, dict) else response_data
        logger.warning(
            "%s Something went wrong fetching group roles: %s",
            response.status_code,
            response.content,
        )
        return None

    def add_parent_group(self, group_id: int, parent_group_id: int) -> bool:
        """Add a parent group for a group.

        Arguments:
            group_id: required group id
            parent_group_id: required parent group id

        Required Permissions:
            administer groups

        Returns:
        True if successful
        """
        url = self.domain + f"/api/groups/{group_id}/parents/{parent_group_id}"
        response = self.session.put(url=url)

        if response.status_code == 201:
            logger.debug("First response of Add Parent Group successful")
            return True
        logger.warning(
            "%s Something went wrong adding parent group: %s",
            response.status_code,
            response.content,
        )
        return None

    def remove_parent_group(self, group_id: int, parent_group_id: int) -> bool:
        """Remove a parent group from a group.

        Arguments:
            group_id: required group id
            parent_group_id: required parent group id

        Returns:
        True if successful
        """
        url = self.domain + f"/api/groups/{group_id}/parents/{parent_group_id}"
        response = self.session.delete(url=url)

        if response.status_code == 204:
            logger.debug("First response of Remove Parent Group successful")
            return True
        logger.warning(
            "%s Something went wrong removing parent group: %s",
            response.status_code,
            response.content,
        )
        return None
