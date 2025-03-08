"""module test groups."""

import json
import logging
import logging.config
from pathlib import Path

import pytest

from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestChurchtoolsApiGroups(TestsChurchToolsApiAbstract):
    """Test for Groups."""

    def test_get_groups(self) -> None:
        """Checks get_groups.

        1. Test requests all groups and checks that result has more than 50 elements
            (hence default pagination works)
        2. Test requests group 103 and checks that result matches Test song.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        groups = self.api.get_groups()
        assert isinstance(groups, list)
        assert isinstance(groups[0], dict)

        EXPECTED_MIN_NUMBER_OF_GROUPS = 10
        assert len(groups) > EXPECTED_MIN_NUMBER_OF_GROUPS

        SAMPLE_GROUP_ID = 103
        groups = self.api.get_groups(group_id=SAMPLE_GROUP_ID)
        assert isinstance(groups, list)
        group = groups[0]
        assert isinstance(group, dict)
        assert group["id"] == SAMPLE_GROUP_ID
        assert group["name"] == "TestGruppe"

    def test_get_groups_hierarchies(self) -> None:
        """Checks that the list of group hierarchies can be retrieved.

        and each element contains the keys 'groupId', 'parents' and 'children'.
        The list should be accessible as dict using groupID as key.
        """
        hierarchies = self.api.get_groups_hierarchies()
        assert isinstance(hierarchies, dict)
        for hierarchy in hierarchies.values():
            assert "groupId" in hierarchy
            assert "parents" in hierarchy
            assert "children" in hierarchy

    def test_get_group_statistics(self) -> None:
        """Checks that the statistics for a group.

        can be retrieved and certain keys
        exist in the dict.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103

        stats = self.api.get_group_statistics(group_id=SAMPLE_GROUP_ID)
        assert stats is not None
        assert "unfiltered" in stats
        assert "freePlaces" in stats["unfiltered"]
        assert "takenPlaces" in stats["unfiltered"]

    def test_get_grouptypes(self) -> None:
        """Test related to grouptypes.

        1. Check that the list of grouptypes can be retrieved and each element contains
        the keys 'id' and 'name'.
        2. Check that a single grouptype can be retrieved and id and name are matching.
        IMPORTANT - This test method and the parameters used depend on target system!
        """
        # multiple group types
        grouptypes = self.api.get_grouptypes()
        assert isinstance(grouptypes, dict)
        EXPECTED_MIN_NUMBER_OF_GROUPTYPES = 2
        assert len(grouptypes) > EXPECTED_MIN_NUMBER_OF_GROUPTYPES
        for grouptype in grouptypes.values():
            assert "id" in grouptype
            assert "name" in grouptype

        # one type only
        EXPECTED_SAMPLE_GROUPTYPE = {2: "Dienst"}

        grouptypes = self.api.get_grouptypes(grouptype_id=2)
        assert len(grouptypes) == 1
        for grouptype in grouptypes.values():
            assert "id" in grouptype
            assert "name" in grouptype
            assert grouptype["id"] == next(iter(EXPECTED_SAMPLE_GROUPTYPE))
            assert grouptype["name"] == next(iter(EXPECTED_SAMPLE_GROUPTYPE.values()))

    def test_get_group_permissions(self) -> None:
        """Checks that the permissions for a group.

        can be retrieved and matches the test permissions.
        IMPORTANT - This test method and the parameters used depend on target system!
        """
        SAMPLE_GROUP_ID = 103
        EXPECTED_NUMNER_OF_PERMISSIONS = 2

        permissions = self.api.get_group_permissions(group_id=SAMPLE_GROUP_ID)
        assert permissions["churchdb"]["+see group"] == EXPECTED_NUMNER_OF_PERMISSIONS
        assert permissions["churchdb"]["+edit group infos"]

    def test_create_and_delete_group(self, caplog: pytest.LogCaptureFixture) -> None:
        """Checks if groups can be created.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.


        1.  with minimal parameters.
        2. More complex group information
        3. Checks if a group can not be created with name of an existing group
        4. same as 3. but should be possible when the 'force' parameter is set.
        5. Checks if groups can be deleted.
        """
        SAMPLE_NEW_GROUP_TYPE = 2
        SAMPLE_GROUP_STATUS_ID = 1
        SAMPLE_CAMPUS_ID = 0

        # 1. minimal group
        SAMPLE_GROUP_NAME = "TestGroup"

        group1 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
        )
        assert group1 is not None
        assert group1["name"] == SAMPLE_GROUP_NAME
        assert group1["information"]["groupTypeId"] == SAMPLE_NEW_GROUP_TYPE
        assert group1["information"]["groupStatusId"] == SAMPLE_GROUP_STATUS_ID

        # 2. more complex group
        SAMPLE_GROUP_NAME2 = "TestGroup With Campus And Superior"
        group2 = self.api.create_group(
            SAMPLE_GROUP_NAME2,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            campus_id=SAMPLE_CAMPUS_ID,
            superior_group_id=group1["id"],
        )
        assert group2 is not None
        assert group2["name"] == SAMPLE_GROUP_NAME2
        assert group2["information"]["groupTypeId"] == SAMPLE_NEW_GROUP_TYPE
        assert group2["information"]["groupStatusId"] == SAMPLE_GROUP_STATUS_ID
        assert group2["information"]["campusId"] == SAMPLE_CAMPUS_ID

        # 3. check force param - only created if forced
        caplog.clear()
        with caplog.at_level(level=logging.WARNING, logger="churchtools_api.groups"):
            group3 = self.api.create_group(
                SAMPLE_GROUP_NAME,
                group_status_id=SAMPLE_GROUP_STATUS_ID,
                grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            )
        assert group3 is None
        EXPECTED_MESSAGES = [
            'Duplikat gefunden. Nutze das "force" Flag, um'
            " die Gruppe trotzdem anzulegen."
        ]
        assert caplog.messages == EXPECTED_MESSAGES

        # 4. use force param to overwrite existing group
        group3 = self.api.create_group(
            SAMPLE_GROUP_NAME,
            group_status_id=SAMPLE_GROUP_STATUS_ID,
            grouptype_id=SAMPLE_NEW_GROUP_TYPE,
            force=True,
        )
        assert group3 is not None
        assert group3["name"] == SAMPLE_GROUP_NAME
        assert group3["information"]["groupTypeId"] == SAMPLE_NEW_GROUP_TYPE
        assert group3["information"]["groupStatusId"] == SAMPLE_GROUP_STATUS_ID

        # 5 .cleanup after testing
        ret = self.api.delete_group(group_id=group1["id"])
        assert ret

        ret = self.api.delete_group(group_id=group2["id"])
        assert ret

        ret = self.api.delete_group(group_id=group3["id"])
        assert ret

    def test_update_group(self) -> None:
        """Checks that a field in a group can be set.

        to some value and the returned group has this field value set.
        Also cleans the field after executing the test

        IMPORTANT - This test method and the parameters used depend on target system!
        The user needs to be able to change group information -
        usually "Leiter" permission enables this.
        """
        SAMPLE_GROUP_ID = 103
        data = {"note": "TestNote - if this exists an automated test case failed"}
        group_update_result = self.api.update_group(group_id=SAMPLE_GROUP_ID, data=data)
        assert group_update_result["information"]["note"] == data["note"]

        group_update_result = self.api.update_group(
            group_id=SAMPLE_GROUP_ID,
            data={"note": ""},
        )
        groups = self.api.get_groups(group_id=SAMPLE_GROUP_ID)
        assert groups[0]["information"]["note"] == ""

    def test_get_group_members(self) -> None:
        """Checks if group members can be retrieved.

        from the group and filtering for role ids works.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_GROUPTYPE_ROLE_ID = 16
        members = self.api.get_group_members(group_id=SAMPLE_GROUP_ID)

        assert members is not None
        assert members != []
        for member in members:
            assert "personId" in member

        members = self.api.get_group_members(
            group_id=SAMPLE_GROUP_ID,
            role_ids=[SAMPLE_GROUPTYPE_ROLE_ID],
        )
        assert members is not None
        assert members != []
        for member in members:
            assert "personId" in member
            assert member["groupTypeRoleId"] == SAMPLE_GROUPTYPE_ROLE_ID

    def test_get_group_memberfields(self) -> None:
        """Checks if group member fields can be retrieved.

        from the group.
        
        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 462
        memberfields = self.api.get_group_memberfields(group_id=SAMPLE_GROUP_ID)

        assert memberfields is not None
        assert memberfields != []
        for memberfield in memberfields:
            assert "type" in memberfield
            assert "id" in memberfield["field"]

    def test_get_groups_members(self) -> None:
        """Check that a list of groups is received.

        when asking by person and optional role id.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_PERSON_IDS = [513]
        SAMPLE_ROLE_ID_LEAD = 16
        SAMPLE_ROLE_ID_MEMBER = 15
        EXPECTED_GROUP_ID = 103  # a services test group

        # 1. person only
        group_result = self.api.get_groups_members(person_ids=SAMPLE_PERSON_IDS)
        compare_result = [group["groupId"] for group in group_result]
        assert EXPECTED_GROUP_ID in compare_result

        # 2a. person user and role - non lead - no group
        group_result = self.api.get_groups_members(
            person_ids=SAMPLE_PERSON_IDS,
            grouptype_role_ids=[SAMPLE_ROLE_ID_MEMBER],
        )
        assert len(group_result) == 0

        # 2b. person and role - lead and non lead
        group_result = self.api.get_groups_members(
            person_ids=SAMPLE_PERSON_IDS,
            groupTypeRoleId=[SAMPLE_ROLE_ID_LEAD, SAMPLE_ROLE_ID_MEMBER],
        )
        assert isinstance(group_result, list)
        assert len(group_result) > 0
        assert isinstance(group_result[0], dict)

        compare_result = [group["groupId"] for group in group_result]
        assert EXPECTED_GROUP_ID in compare_result

        # 3. problematic result group_ids, grouptype_role_ids and person_id
        SAMPLE_GROUP_IDS = [99, 68, 93]
        SAMPLE_GROUPTYPE_ROLE_IDS = [9, 16]
        SAMPLE_PERSON_IDS = [54]

        result = self.api.get_groups_members(
            group_ids=SAMPLE_GROUP_IDS,
            grouptype_role_ids=SAMPLE_GROUPTYPE_ROLE_IDS,
            person_ids=SAMPLE_PERSON_IDS,
        )
        assert len(result) == 1

    def test_add_and_remove_group_members(self) -> None:
        """Checks add_and_remove_group_members.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_PERSON_ID = 229
        SAMPLE_GROUPTYPE_ROLE_ID = 15

        member = self.api.add_group_member(
            group_id=SAMPLE_GROUP_ID,
            person_id=SAMPLE_PERSON_ID,
            grouptype_role_id=SAMPLE_GROUPTYPE_ROLE_ID,
            group_member_status="active",
        )
        assert member is not None
        assert member["personId"] == SAMPLE_PERSON_ID
        assert member["groupTypeRoleId"] == SAMPLE_GROUPTYPE_ROLE_ID
        assert member["groupMemberStatus"] == "active"

        result = self.api.remove_group_member(
            group_id=SAMPLE_GROUP_ID,
            person_id=SAMPLE_PERSON_ID,
        )
        assert result

    def test_get_group_roles(self) -> None:
        """Checks if group roles can be retrieved from a group."""
        SAMPLE_GROUP_ID = 103
        roles = self.api.get_group_roles(group_id=SAMPLE_GROUP_ID)
        assert roles is not None
        assert roles != []
        for role in roles:
            assert "id" in role
            assert "groupTypeId" in role
            assert "name" in role

    def test_add_and_remove_parent_group(self) -> None:
        """Checks if a parent group can be added to and removed from a group.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_GROUP_ID = 103
        SAMPLE_PARENT_GROUP_ID = 50
        result = self.api.add_parent_group(
            group_id=SAMPLE_GROUP_ID,
            parent_group_id=SAMPLE_PARENT_GROUP_ID,
        )
        assert result

        result = self.api.remove_parent_group(
            group_id=SAMPLE_GROUP_ID,
            parent_group_id=SAMPLE_PARENT_GROUP_ID,
        )
        assert result
