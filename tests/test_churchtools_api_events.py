"""module test event."""

import json
import logging
import logging.config
import os
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import pytz
from tzlocal import get_localzone

from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestsChurchToolsApiEvents(TestsChurchToolsApiAbstract):
    """Test for Events."""

    def test_get_events(self, caplog: pytest.LogCaptureFixture) -> None:
        """Tries to get a list of events and a single event from CT.

        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event
        with schedule (20th. Nov 2022)
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
        today_date = datetime.today().astimezone(get_localzone()).date()
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
        caplog.clear()
        with caplog.at_level(level=logging.WARNING, logger="churchtools_api.events"):
            self.api.get_events(to_=next2_week_formatted)
        EXPECTED_MESSAGES = ["Use of to_ is only allowed together with from_"]
        assert caplog.messages == EXPECTED_MESSAGES

        # load more than 10 events (pagination)
        # #TODO @benste: improve test case for pagination
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/1
        EXPECTED_PAGINATION = 11
        result = self.api.get_events(direction="forward", limit=EXPECTED_PAGINATION)
        assert isinstance(result, list)
        assert len(result) >= EXPECTED_PAGINATION

        # TODO @benste: add test cases for uncommon parts (canceled, include)
        # https://github.com/bensteUEM/ChurchToolsAPI/issues/24

    def test_get_set_event_services_counts(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on target system!

        Test function for get and set methods related to event services counts
        tries to get the number of specicifc service in an id
        tries to increase that number
        tries to get the number again
        tries to set it back to original
        On ELKW1610.KRZ.TOOLS event ID 2626 is an existing test Event
        with schedule (1. Jan 2023)
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
        """IMPORTANT - This test method and the parameters used depend on target system!

        Test function to get list of event admins, change it
        and check again (and reset to original)
        On ELKW1610.KRZ.TOOLS event ID 3348 is an existing
        Event with schedule (29. Sept 2024)
        """
        SAMPLE_EVENT_ID = 3348
        EXPECTED_ADMIN_IDS = [336]

        # check initial state
        check_event = self.api.get_events(eventId=SAMPLE_EVENT_ID)[0]
        assert set(check_event["adminIds"]) == set(EXPECTED_ADMIN_IDS)

        # modify param and check it's applied
        SAMPLE_ADMIN_IDS_CHANGED = [1, 2]
        result = self.api.update_event(
            event_id=SAMPLE_EVENT_ID, admin_ids=SAMPLE_ADMIN_IDS_CHANGED
        )
        assert result

        check_event = self.api.get_events(eventId=SAMPLE_EVENT_ID)[0]
        assert set(check_event["adminIds"]) == set(SAMPLE_ADMIN_IDS_CHANGED)

        # reset to original state
        result = self.api.update_event(
            event_id=SAMPLE_EVENT_ID, admin_ids=EXPECTED_ADMIN_IDS
        )
        assert result

        check_event = self.api.get_events(eventId=SAMPLE_EVENT_ID)[0]
        assert set(check_event["adminIds"]) == set(EXPECTED_ADMIN_IDS)

    @pytest.mark.parametrize(
        ("expected_key"),
        [
            "absenceReasons",
            "facts",
            "songCategories",
            "songSources",
            "services",
            "serviceGroups",
        ],
    )
    def test_get_event_masterdata_all(self, expected_key: str) -> None:
        """Tries to get a list of event masterdata and a type of masterdata from CT.

        Categories should exist on all systems with CT version 116 or newer

        Args:
            expected_key: the expected key
        """
        result_all = self.api.get_event_masterdata()
        result_specific = self.api.get_event_masterdata(resultClass=expected_key)
        assert expected_key in result_all
        assert len(result_specific) >= 1

    def test_get_event_masterdata_specific(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on target system!

        Tries to get a list of event masterdata and a type of masterdata from CT
        The values depend on your system data! -
        Test case is valid against ELKW1610.KRZ.TOOLS
        """
        result = self.api.get_event_masterdata(resultClass="serviceGroups")
        assert len(result) > 1
        assert result[0]["name"] == "Programm"

        result = self.api.get_event_masterdata(
            resultClass="serviceGroups", returnAsDict=True
        )
        assert isinstance(result, dict)
        result = self.api.get_event_masterdata(
            resultClass="serviceGroups", returnAsDict=False
        )
        assert isinstance(result, list)

    def test_get_event_agenda(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on target system!

        Tries to get an event agenda from a CT Event
        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event
        with schedule (20th. Nov 2022)
        """
        eventId = 484
        result = self.api.get_event_agenda(eventId)
        assert result is not None

    def test_export_event_agenda(self, caplog: pytest.LogCaptureFixture) -> None:
        """IMPORTANT - This test method and the parameters used depend on target system!

        Test function to download an Event Agenda file package for e.g. Songbeamer
        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event
            with schedule (20th. Nov 2022)
        """
        eventId = 484
        agendaId = self.api.get_event_agenda(eventId)["id"]

        caplog.clear()
        with caplog.at_level(level=logging.WARNING, logger="churchtools_api.events"):
            download_result = self.api.export_event_agenda("SONG_BEAMER")
        assert len(caplog.records) == 1
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

        EXPECTED_NUMBER_OF_FILES = 2
        assert len(os.listdir("downloads")) == EXPECTED_NUMBER_OF_FILES

    def test_get_services(self) -> None:
        """Tries to get all and a single services configuration from the server.

        serviceId varies depending on the server used id 1 = Predigt
            and more than one item exsits
        On any KRZ.TOOLS serviceId 1 is named 'Predigt' and more than one
            service exists by default (13. Jan 2023)
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

    def test_has_event_schedule(self) -> None:
        """Tries to get boolean if event agenda exists for a CT Event.

        Event ID may vary depending on the server used
        On ELKW1610.KRZ.TOOLS event ID 484 is an existing Event
            with schedule (20th. Nov 2022) 2376 does not have one.
        """
        eventId = 484
        result = self.api.get_event_agenda(eventId)
        assert result is not None
        eventId = 2376
        result = self.api.get_event_agenda(eventId)
        assert result is None

    def test_get_event_by_calendar_appointment(self) -> None:
        """Check that event can be retrieved based on known calendar entry.

        On ELKW1610.KRZ.TOOLS (26th. Nov 2023) sample is
        event_id:2261
        appointment:304976 starts on 2023-11-26T09:00:00Z.
        """
        event_id = 2261
        appointment_id = 304976
        start_date = "2023-11-26T09:00:00Z"
        start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").astimezone(
            pytz.timezone("Europe/Berlin")
        )

        result = self.api.get_event_by_calendar_appointment(appointment_id, start_date)
        assert event_id == result["id"]

    def test_get_event_by_calendar_appointment_dateonly(self) -> None:
        """Check that event can be retrieved based on known calendar entry .

        using date only instead of full datetime

        On ELKW1610.KRZ.TOOLS (26th. Nov 2023) sample is
        event_id:4060
        appointment:331150 starts on 2025-03-30T10:00:00Z. (CEST)
        """
        event_id = 4060
        appointment_id = 331150
        start_date = datetime(2025, 3, 30).astimezone(pytz.timezone("Europe/Berlin"))

        result = self.api.get_event_by_calendar_appointment(appointment_id, start_date)
        assert event_id == result["id"]

    def test_get_persons_with_service(self) -> None:
        """Tries to retrieve persons with specific service.

        IMPORTANT - This test method and the parameters used depend on target system!
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
