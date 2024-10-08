import ast
import json
import logging
import logging.config
import os
import unittest
from datetime import datetime, timedelta
from pathlib import Path

from churchtools_api.churchtools_api import ChurchToolsApi

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestsChurchToolsApi(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if "CT_TOKEN" in os.environ:
            self.ct_token = os.environ["CT_TOKEN"]
            self.ct_domain = os.environ["CT_DOMAIN"]
            users_string = os.environ["CT_USERS"]
            self.ct_users = ast.literal_eval(users_string)
            logger.info("using connection details provided with ENV variables")
        else:
            from secure.config import ct_token

            self.ct_token = ct_token
            from secure.config import ct_domain

            self.ct_domain = ct_domain
            from secure.config import ct_users

            self.ct_users = ct_users
            logger.info("using connection details provided from secrets folder")

        self.api = ChurchToolsApi(domain=self.ct_domain, ct_token=self.ct_token)
        logger.info("Executing Tests RUN")

    def tearDown(self) -> None:
        """Destroy the session after test execution to avoid resource issues
        :return:
        """
        self.api.session.close()

    def test_get_events(self) -> None:
        """Tries to get a list of events and a single event from CT.

        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event with schedule (20th. Nov 2022)
        :return:
        """
        result = self.api.get_events()
        assert result is not None
        assert isinstance(result, list)

        eventId = 484
        result = self.api.get_events(eventId=eventId)
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)

        # load next event (limit)
        result = self.api.get_events(limit=1, direction="forward")
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        result_date = (
            datetime.strptime(result[0]["startDate"], "%Y-%m-%dT%H:%M:%S%z")
            .astimezone()
            .date()
        )
        today_date = datetime.today().date()
        assert result_date >= today_date

        # load last event (direction, limit)
        result = self.api.get_events(limit=1, direction="backward")
        result_date = (
            datetime.strptime(result[0]["startDate"], "%Y-%m-%dT%H:%M:%S%z")
            .astimezone()
            .date()
        )
        assert result_date <= today_date

        # Load events after 7 days (from)
        next_week_date = today_date + timedelta(days=7)
        next_week_formatted = next_week_date.strftime("%Y-%m-%d")
        result = self.api.get_events(from_=next_week_formatted)
        result_min_date = min(
            [
                datetime.strptime(item["startDate"], "%Y-%m-%dT%H:%M:%S%z")
                .astimezone()
                .date()
                for item in result
            ],
        )
        result_max_date = max(
            [
                datetime.strptime(item["startDate"], "%Y-%m-%dT%H:%M:%S%z")
                .astimezone()
                .date()
                for item in result
            ],
        )
        assert result_min_date >= next_week_date
        assert result_max_date >= next_week_date

        # load events for next 14 days (to)
        next2_week_date = today_date + timedelta(days=14)
        next2_week_formatted = next2_week_date.strftime("%Y-%m-%d")
        today_date_formatted = today_date.strftime("%Y-%m-%d")

        result = self.api.get_events(
            from_=today_date_formatted,
            to_=next2_week_formatted,
        )
        result_min = min(
            [
                datetime.strptime(item["startDate"], "%Y-%m-%dT%H:%M:%S%z")
                .astimezone()
                .date()
                for item in result
            ],
        )
        result_max = max(
            [
                datetime.strptime(item["startDate"], "%Y-%m-%dT%H:%M:%S%z")
                .astimezone()
                .date()
                for item in result
            ],
        )
        # only works if there is an event within 7 days on demo system
        assert result_min <= next_week_date
        assert result_max <= next2_week_date

        # missing keyword pair warning
        with self.assertLogs(level=logging.WARNING) as captured:
            self.api.get_events(to_=next2_week_formatted)
        assert len(captured.records) == 1
        assert captured.output == [
            "WARNING:churchtools_api.events:Use of to_ is only allowed together with from_"
        ]

        # load more than 10 events (pagination #TODO #1 improve test case for
        # pagination
        result = self.api.get_events(direction="forward", limit=11)
        assert isinstance(result, list)
        assert len(result) >= 11

        # TODO add test cases for uncommon parts #24 * canceled, include

    def test_get_AllEventData_ajax(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Test function to check the get_AllEventData_ajax function for a specific ID
        On ELKW1610.KRZ.TOOLS event ID 3348 is an existing Test Event with schedule (29. Sept 2024)
        Please be aware that this function is limited to the timeframe configured for cache in CT (by default -90days)
        :return:
        """
        SAMPLE_EVENT_ID = 3348
        result = self.api.get_AllEventData_ajax(SAMPLE_EVENT_ID)
        assert "id" in result
        assert result["id"] == str(SAMPLE_EVENT_ID)

    def test_get_set_event_services_counts(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Test function for get and set methods related to event services counts
        tries to get the number of specicifc service in an id
        tries to increase that number
        tries to get the number again
        tries to set it back to original
        On ELKW1610.KRZ.TOOLS event ID 2626 is an existing test Event with schedule (1. Jan 2023)
        On ELKW1610.KRZ.TOOLS serviceID 1 is Predigt (1. Jan 2023)
        :return:
        """
        eventId = 2626
        serviceId = 1
        original_count_comapre = 3

        self.api.get_events(eventId=eventId)

        original_count = self.api.get_event_services_counts_ajax(
            eventId=eventId,
            serviceId=serviceId,
        )
        assert original_count == {serviceId: original_count_comapre}

        result = self.api.set_event_services_counts_ajax(eventId, serviceId, 2)
        assert result

        new_count = self.api.get_event_services_counts_ajax(
            eventId=eventId,
            serviceId=serviceId,
        )
        assert new_count == {serviceId: 2}

        result = self.api.set_event_services_counts_ajax(
            eventId,
            serviceId,
            original_count[serviceId],
        )
        assert result

    def test_get_set_event_admins(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Test function to get list of event admins, change it and check again (and reset to original)
        On ELKW1610.KRZ.TOOLS event ID 3348 is an existing Event with schedule (29. Sept 2024)
        Please be aware that this function is limited to the timeframe configured for cache in CT (by default -90days)
        :return:
        """
        SAMPLE_EVENT_ID = 3348
        EXPECTED_ADMIN_IDS = [336]

        admin_ids_original = self.api.get_event_admins_ajax(SAMPLE_EVENT_ID)
        assert admin_ids_original == EXPECTED_ADMIN_IDS

        admin_ids_change = [0, 1, 2]
        result = self.api.set_event_admins_ajax(SAMPLE_EVENT_ID, admin_ids_change)
        assert result

        admin_ids_test = self.api.get_event_admins_ajax(SAMPLE_EVENT_ID)
        assert admin_ids_change == admin_ids_test

        assert self.api.set_event_admins_ajax(SAMPLE_EVENT_ID, EXPECTED_ADMIN_IDS)

    def test_get_event_masterdata(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Tries to get a list of event masterdata and a type of masterdata from CT
        The values depend on your system data! - Test case is valid against ELKW1610.KRZ.TOOLS
        :return:
        """
        result = self.api.get_event_masterdata()
        assert len(result) == 5

        result = self.api.get_event_masterdata(type="serviceGroups")
        assert len(result) > 1
        assert result[0]["name"] == "Programm"

        result = self.api.get_event_masterdata(type="serviceGroups", returnAsDict=True)
        assert isinstance(result, dict)
        result = self.api.get_event_masterdata(type="serviceGroups", returnAsDict=False)
        assert isinstance(result, list)

    def test_get_event_agenda(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Tries to get an event agenda from a CT Event
        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event with schedule (20th. Nov 2022)
        :return:
        """
        eventId = 484
        result = self.api.get_event_agenda(eventId)
        assert result is not None

    def test_export_event_agenda(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Test function to download an Event Agenda file package for e.g. Songbeamer
        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event with schedule (20th. Nov 2022)
        """
        eventId = 484
        agendaId = self.api.get_event_agenda(eventId)["id"]

        with self.assertLogs(level=logging.WARNING) as captured:
            download_result = self.api.export_event_agenda("SONG_BEAMER")
        assert len(captured.records) == 1
        assert not download_result

        download_dir = Path("downloads")
        for root, dirs, files in download_dir.walk(top_down=False):
            for name in files:
                (root / name).unlink()
            for name in dirs:
                (root / name).rmdir()

        download_result = self.api.export_event_agenda("SONG_BEAMER", agendaId=agendaId)
        assert download_result

        download_result = self.api.export_event_agenda("SONG_BEAMER", eventId=eventId)
        assert download_result

        assert len(os.listdir("downloads")) == 2

    def test_get_services(self) -> None:
        """Tries to get all and a single services configuration from the server
        serviceId varies depending on the server used id 1 = Predigt and more than one item exsits
        On any KRZ.TOOLS serviceId 1 is named 'Predigt' and more than one service exists by default (13. Jan 2023)
        :return:
        """
        serviceId = 1
        result1 = self.api.get_services()
        assert isinstance(result1, list)
        assert isinstance(result1[0], dict)
        assert len(result1) > 1

        result2 = self.api.get_services(serviceId=serviceId)
        assert isinstance(result2, dict)
        assert result2["name"] == "Predigt"

        result3 = self.api.get_services(returnAsDict=True)
        assert isinstance(result3, dict)

        result4 = self.api.get_services(returnAsDict=False)
        assert isinstance(result4, list)

    def test_get_tags(self) -> None:
        """Test function for get_tags() with default type song
        On ELKW1610.KRZ.TOOLS tag ID 49 has the name To Do
        :return:
        """
        result = self.api.get_tags()
        assert len(result) > 0
        test_tag = next(item for item in result if item["id"] == 49)
        assert test_tag["id"] == 49
        assert test_tag["name"] == "ToDo"

    def test_has_event_schedule(self) -> None:
        """Tries to get boolean if event agenda exists for a CT Event
        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event with schedule (20th. Nov 2022)
        2376 does not have one
        :return:
        """
        eventId = 484
        result = self.api.get_event_agenda(eventId)
        assert result is not None
        eventId = 2376
        result = self.api.get_event_agenda(eventId)
        assert result is None

    def test_get_event_by_calendar_appointment(self) -> None:
        """Check that event can be retrieved based on known calendar entry
        On ELKW1610.KRZ.TOOLS (26th. Nov 2023) sample is
        event_id:2261
        appointment:304976 starts on 2023-11-26T09:00:00Z.
        """
        event_id = 2261
        appointment_id = 304976
        start_date = "2023-11-26T09:00:00Z"
        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ")

        result = self.api.get_event_by_calendar_appointment(appointment_id, start_date)
        assert event_id == result["id"]

    def test_get_persons_with_service(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        SAMPLE_EVENT_ID = 3348
        SAMPLE_SERVICE_ID = 1

        result = self.api.get_persons_with_service(
            eventId=SAMPLE_EVENT_ID,
            serviceId=SAMPLE_SERVICE_ID,
        )

        assert len(result) >= 1
        assert result[0]["serviceId"] >= 1
