"""module test persons."""

import json
import logging
import logging.config
from datetime import datetime
from pathlib import Path

import pytest
from dateutil.relativedelta import relativedelta
from tzlocal import get_localzone

from churchtools_api.posts import GroupVisibility, PostVisibility
from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestChurchtoolsApiPosts(TestsChurchToolsApiAbstract):
    """Test for Posts."""

    @pytest.mark.skip("not tested")
    def test_get_external_posts(self) -> None:
        """Tries to get a list of external posts.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        EXPECTED_MIN_NUMBER_OF_PERSONS = 1

        result = self.api.get_external_posts()
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert len(result) > EXPECTED_MIN_NUMBER_OF_PERSONS

    def test_get_posts(self) -> None:
        """Tries to get a all posts.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        EXPECTED_MIN_NUMBER_OF_POSTS = 1

        result = self.api.get_posts()
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert len(result) > EXPECTED_MIN_NUMBER_OF_POSTS

    def test_get_posts_paginated(self) -> None:
        """Tries to get a all posts.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        PAGE_LIMIT = 10

        result = self.api.get_posts(limit=PAGE_LIMIT)
        assert isinstance(result, list)
        assert len(result) == PAGE_LIMIT

        result = self.api.get_posts()
        assert isinstance(result, list)
        assert len(result) > PAGE_LIMIT

    def test_get_posts_dates(self) -> None:
        """Tries to get a all posts using date filters.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        At present this requires at least 2 post in last 2 months
        """
        EXPECTED_MIN_NUMBER_OF_POSTS = 2
        FROM_DATE = datetime.now().astimezone(get_localzone()) - relativedelta(months=2)
        TO_DATE = datetime.now().astimezone(get_localzone())

        result = self.api.get_posts(after=FROM_DATE, before=TO_DATE)
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert len(result) >= EXPECTED_MIN_NUMBER_OF_POSTS
        result_all_dates = [
            datetime.strptime(
                post["publishedDate"],
                "%Y-%m-%dT%H:%M:%S%z",
            )
            for post in result
        ]
        assert all(FROM_DATE <= date <= TO_DATE for date in result_all_dates)

    @pytest.mark.skip("issue with CT implementation reported")
    def test_get_posts_before_last_post(self, caplog: pytest.LogCaptureFixture) -> None:
        """Tries to get a all posts using date after filter and last_post_indentifier.

        Also tries to request with missing required dependant param

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        At present this requires at requires two post in Dec 2024
        of which the later one should have the specified ID
        """
        EXPECTED_NUMBER_OF_POSTS = 2
        FROM_DATE = datetime(year=2024, month=12, day=1).astimezone(get_localzone())
        TO_DATE = datetime(year=2024, month=12, day=31).astimezone(get_localzone())
        TO_GUID = "DA9C24AD-27FE-496E-98D0-DF974F4B6F8D"

        result = self.api.get_posts(
            after=FROM_DATE, before=TO_DATE, last_post_indentifier=TO_GUID
        )
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert len(result) >= EXPECTED_NUMBER_OF_POSTS

        # check warning is logged when param is missing
        caplog.clear()
        with caplog.at_level(logging.WARNING, logger="churchtools_api.posts"):
            self.api.get_posts(last_post_indentifier=TO_GUID)
        EXPECTED_MESSAGES = [
            "last post identifier can only be used together with before"
        ]
        assert caplog.messages == EXPECTED_MESSAGES
        # TODO @bensteUEM: issue with CT last_post_ident reported to CT support 137701
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/128

    def test_get_posts_campus_id(self) -> None:
        """Tries to get a all posts using campus_id.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        requires at least 2 posts in campus 0 and no posts in campus 7
        """
        EXPECTED_MIN_NUMBER_OF_POSTS_BY_CAMPUS = {0: 2, 7: 0}
        FROM_DATE = datetime.now().astimezone(get_localzone()) - relativedelta(months=2)
        TO_DATE = datetime.now().astimezone(get_localzone())

        for (
            campus_id,
            exepcted_min_number_of_posts,
        ) in EXPECTED_MIN_NUMBER_OF_POSTS_BY_CAMPUS.items():
            result = self.api.get_posts(
                after=FROM_DATE, before=TO_DATE, campus_ids=[campus_id]
            )
            if exepcted_min_number_of_posts > 0:
                assert isinstance(result, list)
                assert isinstance(result[0], dict)
            assert len(result) >= exepcted_min_number_of_posts

    def test_get_posts_actor_id(self) -> None:
        """Tries to get a all posts using actor_id.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        User 9 has 2 posts from Oct-Dec 2024
        User 629 posted 1time from Oct-Dec 2024
        """
        EXPECTED_MIN_NUMBER_OF_POSTS_BY_ACTOR = {9: 2, 629: 1}
        FROM_DATE = datetime.now().astimezone(get_localzone()) - relativedelta(months=2)
        TO_DATE = datetime.now().astimezone(get_localzone())

        for (
            actor_id,
            exepcted_number_of_posts,
        ) in EXPECTED_MIN_NUMBER_OF_POSTS_BY_ACTOR.items():
            result = self.api.get_posts(
                after=FROM_DATE, before=TO_DATE, actor_ids=[actor_id]
            )
            assert len(result) >= exepcted_number_of_posts

        # combined result
        result = self.api.get_posts(
            after=FROM_DATE,
            before=TO_DATE,
            actor_ids=[EXPECTED_MIN_NUMBER_OF_POSTS_BY_ACTOR.keys()],
        )
        assert len(result) >= sum(EXPECTED_MIN_NUMBER_OF_POSTS_BY_ACTOR.values())

    def test_get_posts_group_visibility(self) -> None:
        """Tries to get a all posts using group_visibility.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        result_hidden = self.api.get_posts(
            group_visibility=GroupVisibility.HIDDEN,
        )

        result_internal = self.api.get_posts(
            group_visibility=GroupVisibility.INTERN,
        )

        result_public = self.api.get_posts(
            group_visibility=GroupVisibility.PUBLIC,
        )

        result_restricted = self.api.get_posts(
            group_visibility=GroupVisibility.RESTRICTED,
        )

        result_any = self.api.get_posts()

        assert (
            len(result_hidden)
            + len(result_internal)
            + len(result_public)
            + len(result_restricted)
        ) == len(result_any)

    def test_get_posts_post_visibility(self) -> None:
        """Tries to get a all posts using post_visibility.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        result_intern = self.api.get_posts(
            post_visibility=PostVisibility.GROUP_INTERN,
        )

        result_visible = self.api.get_posts(
            post_visibility=PostVisibility.GROUP_VISIBLE,
        )

        result_any = self.api.get_posts()

        assert len(result_intern) != len(result_visible)
        assert len(result_intern) + len(result_visible) == len(result_any)

    def test_get_posts_group_ids(self) -> None:
        """Tries to get a all posts using group_ids.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        EXPECTED_GROUPS = [68]

        result = self.api.get_posts(
            group_ids=EXPECTED_GROUPS,
        )

        assert all(
            int(group["group"]["domainIdentifier"]) in EXPECTED_GROUPS
            for group in result
        )

    @pytest.mark.parametrize(
        "include_sections",
        [(["comments"]), (["reactions"]), (["linkings"]), (["comments", "reactions"])],
    )
    def test_get_posts_include(self, include_sections: list[str]) -> None:
        """Tries to get any posts with different includes.

        Args:
            include_sections: parametrized sections that should be included
        """
        result = self.api.get_posts(
            include=include_sections,
        )

        assert all(expected_key in result[0] for expected_key in include_sections)

    def test_get_posts_only_my_groups(self) -> None:
        """Tries retrieve posts and limit to user groups only."""
        result_only = self.api.get_posts(
            only_my_groups=True,
        )
        result_any = self.api.get_posts(
            only_my_groups=False,
        )

        assert len(result_only) != len(result_any)
