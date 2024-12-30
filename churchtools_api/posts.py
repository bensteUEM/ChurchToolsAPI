"""module containing parts used for posts handling."""

import json
import logging
from datetime import datetime
from enum import Enum

import pytz
import requests

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract

logger = logging.getLogger(__name__)


class GroupVisibility(Enum):
    """Possible values for group visibility option of posts."""

    ANY = None
    HIDDEN = "hidden"
    INTERN = "intern"
    PUBLIC = "public"
    RESTRICTED = "restricted"


class PostVisibility(Enum):
    """Possible values for post visibility option of posts."""

    ANY = None
    GROUP_VISIBLE = "group_visible"
    GROUP_INTERN = "group_intern"


class ChurchToolsApiPosts(ChurchToolsApiAbstract):
    """Part definition of ChurchToolsApi which focuses on posts.

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self) -> None:
        """Inherited initialization."""
        super()

    def get_posts(  # noqa: C901, PLR0912, PLR0913
        self,
        *,
        before: datetime | None = None,
        last_post_indentifier: str | None = None,
        after: datetime | None = None,
        campus_ids: list[int] | None = None,
        actor_ids: list[int] | None = None,
        group_visibility: GroupVisibility = GroupVisibility.ANY,
        post_visibility: PostVisibility = PostVisibility.ANY,
        group_ids: list[int] | None = None,
        include: list[str] | None = None,
        limit: int = 10,
        only_my_groups: bool = False,
    ) -> list[dict]:
        """Retrieve posts applying all optionally defined arguments.

        Args:
            before: last date to include. Defaults to Any.
            last_post_indentifier: GUID of max post to display. Defaults to Any.
            after: _first date to include. Defaults to Any.
            campus_ids: list of campus_ids to include. Defaults to Any.
            actor_ids: list of person ids that created the post. Defaults to Any.
            group_visibility: filter to one respective group visibility option.
                Defaults to GroupVisibility.ANY.
            post_visibility: filter to one specific post visibility option only.
                Defaults to PostVisibility.ANY.
            group_ids: group ids to take into account. Defaults to Any.
            include: more details to include in response. Defaults to None.
                known values are "comments", "reactions" and "linkings"
            limit: pagination used. Defaults to 10.
            only_my_groups: limit results to groups that the requesting user is part of.
                Defaults to False.

        Returns:
            List of posts
        """
        url = self.domain + "/api/posts"
        params = {"limit": limit}

        if after:
            params["after"] = (
                after.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            )
        if before:
            params["before"] = (
                before.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S") + "Z",
            )
            if last_post_indentifier:
                params["last_post_indentifier"] = last_post_indentifier
                # TODO @bensteUEM: issue with CT last_post_ident CT support 137701
                # https://github.com/bensteUEM/ChurchToolsAPI/issues/128
                logger.warning(
                    "there might be an issue with the CT API - reported as support case"
                )
        elif last_post_indentifier:
            logger.warning("last post identifier can only be used together with before")

        # CT API also knows campus_id but this seems to be redundant
        if campus_ids:
            params["campus_ids[]"] = campus_ids

        if actor_ids:
            params["actor_ids[]"] = actor_ids

        if group_visibility:
            params["group_visibility"] = group_visibility.value

        if post_visibility:
            params["post_visibility"] = post_visibility.value

        if group_ids:
            params["group_ids[]"] = group_ids

        if include:
            params["include[]"] = include

        if only_my_groups:
            params["only_my_groups"] = only_my_groups

        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            logger.debug(
                "len of first response of GET posts successful len(%s)",
                response_content,
            )

            if len(response_data) == 0:
                logger.warning(
                    "Requesting posts %s returned an empty response - "
                    "make sure the filters match content",
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

            logger.debug("Posts load successful len=%s", len(response_data))
            return response_data

        logger.info("Posts requested failed: %s", response.status_code)
        return None

    def get_external_posts(self, *, limit: int = 10) -> list[dict]:
        """Function to get list of all external posts from CT.

        Arguments:
            limit: number of items to use
        Returns:
            list external posts
        """
        exception_message = (
            "External Posts seems to be different from publicly visible"
            "posts therefore was not fully tested"
        )
        raise NotImplementedError(exception_message)
        # TODO @Benedict: Implement external posts
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/128

        url = self.domain + "/api/externalposts"
        params = {"limit": limit}

        headers = {"accept": "application/json"}
        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == requests.codes.ok:
            response_content = json.loads(response.content)
            response_data = response_content["data"].copy()

            logger.debug(
                "len of first response of GET Persons successful len(%s)",
                response_content,
            )

            if len(response_data) == 0:
                logger.warning(
                    "Requesting external posts %s returned an empty response - "
                    "make sure the there are public posts",
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

            logger.debug("Posts load successful %s", response_data)
            return response_data

        logger.info("Posts requested failed: %s", response.status_code)
        return None
