import json
import logging
import logging.config
from datetime import datetime, timedelta
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


class TestsChurchToolsApi(TestsChurchToolsApiAbstract):
    def test_get_calendar(self) -> None:
        """Tries to retrieve a list of calendars."""
        result = self.api.get_calendars()
        assert len(result) >= 1
        assert isinstance(result, list)
        assert "id" in result[0]

    def test_get_calendar_apointments(self) -> None:
        """Tries to retrieve calendar appointments
        IMPORTANT - This test method and the parameters used depend on the target system!
        Requires the connected test system to have a calendar mapped as ID 2 and 42 (or changed if other system)
        Calendar 2 should have 3 appointments on 19.11.2023
        One event should be appointment ID=327032.
        """
        # Multiple calendars

        result = self.api.get_calendar_appointments(calendar_ids=[2, 42])
        assert len(result) >= 1
        assert isinstance(result, list)
        assert "id" in result[0]

        # One calendar with from date only (at least 4 appointments)
        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            from_="2023-11-19",
        )
        assert len(result) > 4
        assert isinstance(result, list)
        assert "id" in result[0]

        # One calendar with from and to date (exactly 4 appointments)
        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            from_="2023-11-19",
            to_="2023-11-19",
        )
        assert len(result) == 3
        assert isinstance(result, list)
        assert "id" in result[0]

        # One event in a calendar
        test_appointment_id = 327032
        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            appointment_id=test_appointment_id,
        )
        assert len(result) == 1
        assert isinstance(result, list)
        assert "id" in result[0]
        assert test_appointment_id == result[0]["id"]

    def test_get_calendar_apointments_datetime(self) -> None:
        """Tries to retrieve calendar appointments using datetime instead of str params
        IMPORTANT - This test method and the parameters used depend on the target system!
        Requires the connected test system to have a calendar mapped as ID 2 (or changed if other system)
        Calendar 2 should have 3 appointments on 19.11.2023
        One event should be appointment ID=327032.
        """
        # One calendar with from and to date (exactly 4 appointments)
        from_ = datetime(year=2023, month=11, day=19)
        to_ = datetime(year=2023, month=11, day=19)
        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            from_=from_,
            to_=to_,
        )
        assert len(result) == 3
        assert isinstance(result, list)
        assert "id" in result[0]

    def test_get_calendar_appoints_on_seriess(self) -> None:
        """This test should check the behaviour of get_calendar_appointments on a series
        IMPORTANT - This test method and the parameters used depend on the target system!
        Requires the connected test system to have a calendar mapped as ID 2
        Calendar 2 should have appointment 304973 with an instance of series on 26.11.2023.
        """
        # Appointment Series by ID
        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            appointment_id=304973,
        )
        assert result[0]["appointment"]["caption"] == "Gottesdienst Friedrichstal"
        assert result[0]["appointment"]["startDate"] == "2023-01-08T08:00:00Z"
        assert result[0]["appointment"]["endDate"] == "2023-01-08T09:00:00Z"

        # Appointment Instance by timeframe
        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            from_="2023-11-26",
            to_="2023-11-26",
        )
        result = [
            appointment
            for appointment in result
            if appointment["caption"] == "Gottesdienst Friedrichstal"
        ]
        assert result[0]["caption"] == "Gottesdienst Friedrichstal"
        assert result[0]["startDate"] == "2023-11-26T08:00:00Z"
        assert result[0]["endDate"] == "2023-11-26T09:00:00Z"

        # Multiple appointment Instances by timeframe

        result = self.api.get_calendar_appointments(
            calendar_ids=[2],
            from_="2023-11-19",
            to_="2023-11-26",
        )
        result = [
            appointment
            for appointment in result
            if appointment["caption"] == "Gottesdienst Friedrichstal"
        ]
        assert len(result) == 2
        assert result[-1]["caption"] == "Gottesdienst Friedrichstal"
        assert result[-1]["startDate"] == "2023-11-26T08:00:00Z"
        assert result[-1]["endDate"] == "2023-11-26T09:00:00Z"

    def test_get_calendar_appointments_none(self) -> None:
        """Check that there is no error if no item can be found
        There should be no calendar appointments on the specified day.
        """
        # Appointment Series by ID
        result = self.api.get_calendar_appointments(
            calendar_ids=[52],
            from_="2023-12-01",
            to_="2023-12-02",
        )

        assert result is None

    def test_create_edit_delete_calendar_appointment(self, caplog):
        """Creates, update and deletes a calendar appointment.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        SAMPLE_CALENDAR = (
            45  # non public sample calendar id which exists on test system
        )
        SAMPLE_DATA = {
            "startDate": datetime.now(),
            "endDate": datetime.now() + timedelta(minutes=10),
            "title": "test_title",
            "subtitle": "test_subtitle",
            "description": "test_description long",
            "isInternal": False,
            "address": {
                "addition": "string",
                "city": "Baiersbronn",
                "district": "string",
                "latitude": "string",
                "longitude": "string",
                "meetingAt": "string",
                "street": "Oberdorfstraße 59",
                "zip": "72270",  # TODO must be without last ,
            },
            "link": "string",
        }
        # 1. create
        calendar_appointment = self.api.create_calender_appointment(
            calendar_id=SAMPLE_CALENDAR,
            startDate=SAMPLE_DATA.get("startDate"),
            endDate=SAMPLE_DATA.get("endDate"),
            title=SAMPLE_DATA.get("title"),
            subtitle=SAMPLE_DATA.get("subtitle"),
            description=SAMPLE_DATA.get("description"),
            isInternal=SAMPLE_DATA.get("isInternal"),
            address=SAMPLE_DATA.get("address"),
            link=SAMPLE_DATA.get("link"),
        )
        appointment_id = calendar_appointment["id"]

        check_appointment = self.api.get_calendar_appointments(
            calendar_ids=[SAMPLE_CALENDAR], appointment_id=appointment_id
        )[0]
        for expected_key, expected_value in SAMPLE_DATA.items():
            if expected_key in ["startDate", "endDate"]:
                assert (
                    check_appointment[expected_key]
                    == expected_value.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
                )
            elif expected_key == "address":
                for (
                    expected_address_key,
                    expected_address_value,
                ) in expected_value.items():
                    assert (
                        check_appointment[expected_key][expected_address_key]
                        == expected_address_value
                    )
            else:
                assert check_appointment[expected_key] == expected_value

        # 2a. update one kwarg field
        new_sample_end_date = datetime.now() + timedelta(days=1)
        check_appointment = self.api.update_calender_appointment(
            calendar_id=SAMPLE_CALENDAR,
            appointment_id=appointment_id,
            endDate=new_sample_end_date,
        )
        assert (
            check_appointment["endDate"]
            == new_sample_end_date.strftime("%Y-%m-%dT%H:%M:%S") + "Z"
        )

        # 2b. update subtitle field
        new_sample_subtitle = "updated subtitle"
        check_appointment = self.api.update_calender_appointment(
            calendar_id=SAMPLE_CALENDAR,
            appointment_id=appointment_id,
            subtitle=new_sample_subtitle,
        )
        assert check_appointment["subtitle"] == new_sample_subtitle

        # 2c. update date field
        new_bool = False
        check_appointment = self.api.update_calender_appointment(
            calendar_id=SAMPLE_CALENDAR,
            appointment_id=appointment_id,
            isInternal=new_bool,
        )
        assert check_appointment["isInternal"] == new_bool

        # 2. delete
        self.api.delete_calender_appointment(
            calendar_id=SAMPLE_CALENDAR, appointment_id=appointment_id
        )
        with caplog.at_level(logging.WARNING, logger="churchtools_api.calendar"):
            self.api.get_calendar_appointments(
                calendar_ids=[SAMPLE_CALENDAR], appointment_id=appointment_id
            )

        expected_message = f"appointment [{appointment_id}] not found"
        assert expected_message in caplog.messages[-1]
