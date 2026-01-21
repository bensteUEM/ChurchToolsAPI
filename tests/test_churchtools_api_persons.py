"""module test persons."""

import json
import logging
import logging.config
from pathlib import Path

from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestChurchtoolsApiPersons(TestsChurchToolsApiAbstract):
    """Test for Persons."""

    def test_get_persons(self) -> None:
        """Tries to get all and a single person from the server.

        Be aware that only ct_users that are visible to the user associated
        with the login token can be viewed!

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS

        On any elkw.KRZ.TOOLS personId 1 'firstName' starts with 'Ben'
        and more than 50 ct_users exist(13. Jan 2023)
        """
        EXPECTED_MIN_NUMBER_OF_PERSONS = 50

        personId = 1
        result1 = self.api.get_persons()
        assert isinstance(result1, list)
        assert isinstance(result1[0], dict)
        assert len(result1) > EXPECTED_MIN_NUMBER_OF_PERSONS

        result2 = self.api.get_persons(ids=[personId])
        assert isinstance(result2, list)
        assert isinstance(result2[0], dict)
        assert result2[0]["firstName"][0:3] == "Ben"

        result3 = self.api.get_persons(returnAsDict=True)
        assert isinstance(result3, dict)

        result4 = self.api.get_persons(returnAsDict=False)
        assert isinstance(result4, list)

    def test_get_persons_masterdata(self) -> None:
        """Tries to retrieve metadata for persons module.

        Expected sections equal those that were available
            on ELKW1610.krz.tools on 4.Oct.2024.
        """
        EXPECTED_SECTIONS = {
            "roles",
            "ageGroups",
            "targetGroups",
            "groupTypes",
            "groupCategories",
            "groupStatuses",
            "departments",
            "statuses",
            "campuses",
            "contactLabels",
            "growPaths",
            "followUps",
            "followUpIntervals",
            "groupMeetingTemplates",
            "relationshipTypes",
            "sexes",
        }

        # all items
        result = self.api.get_persons_masterdata()
        assert isinstance(result, dict)
        assert set(result.keys()) == EXPECTED_SECTIONS

        for section in result.values():
            assert isinstance(section, list)
            for item in section:
                assert isinstance(item, dict)

        # only one type
        result = self.api.get_persons_masterdata(resultClass="sexes")
        assert isinstance(result, list)
        assert len(result) > 1
        assert isinstance(next(iter(result)), dict)

        # only one type as dict
        result = self.api.get_persons_masterdata(resultClass="sexes", returnAsDict=True)
        assert isinstance(result, dict)
        assert len(result) > 1
        assert isinstance(next(iter(result.keys())), int)
        assert isinstance(next(iter(result.values())), str)

    def test_get_persons_sex_id(self) -> None:
        """Tests that persons sexId can be retrieved.

        and converted to a human readable gender.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        EXPECTED_RESULT = "sex.unknown"
        SAMPLE_USER_ID = 513

        person = self.api.get_persons(ids=[SAMPLE_USER_ID])[0]
        gender_map = self.api.get_persons_masterdata(
            resultClass="sexes", returnAsDict=True
        )
        result = gender_map[person["sexId"]]

        assert result == EXPECTED_RESULT

    def test_get_persons_sex_id_none(self) -> None:
        """Tests that persons sexId can be converted if NULL.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        EXPECTED_RESULT = "sex.unknown"

        gender_map = self.api.get_persons_masterdata(
            resultClass="sexes", returnAsDict=True
        )
        result = gender_map[None]

        assert result == EXPECTED_RESULT

    def test_create_delete_person(self) -> None:
        """Tests creating and deleting a person.

        IMPORTANT - This test method and the parameters used depend on target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_FIRST_NAME = "TestFirstName"
        SAMPLE_LAST_NAME = "TestLastName"
        SAMPLE_MAIL = "TestMail@Example.com"

        sample_person_data = {
            "firstName": SAMPLE_FIRST_NAME,
            "lastName": SAMPLE_LAST_NAME,
            "email": SAMPLE_MAIL,
        }

        # create person
        new_person = self.api.create_person(sample_person_data)
        assert isinstance(new_person["id"], int)

        # retrieve person and check data
        check_person = self.api.get_persons(ids=[new_person["id"]])[0]
        assert check_person["firstName"] == SAMPLE_FIRST_NAME
        assert check_person["lastName"] == SAMPLE_LAST_NAME
        assert check_person["email"] == SAMPLE_MAIL

        # delete person
        delete_result = self.api.delete_person(personId=new_person["id"])
        assert delete_result is True
