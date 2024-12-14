"""module test resources."""

import json
import logging
import logging.config
from datetime import datetime, timedelta
from pathlib import Path

import pytz

from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract

logger = logging.getLogger(__name__)

config_file = Path("logging_config.json")
with config_file.open(encoding="utf-8") as f_in:
    logging_config = json.load(f_in)
    log_directory = Path(logging_config["handlers"]["file"]["filename"]).parent
    if not log_directory.exists():
        log_directory.mkdir(parents=True)
    logging.config.dictConfig(config=logging_config)


class TestChurchtoolsApiResources(TestsChurchToolsApiAbstract):
    """Test for Resources."""

    def test_get_resource_masterdata(self) -> None:
        """Check resource masterdata can be retrieved."""
        result = self.api.get_resource_masterdata()
        assert isinstance(result, dict)
        EXPECTED_KEYS = {
            "resourceTypes",
            "resources",
        }
        assert set(result.keys()) == EXPECTED_KEYS

    def test_get_resource_masterdata_resourceTypes(self) -> None:
        """Check resourceTypes can be retrieved."""
        result = self.api.get_resource_masterdata(resultClass="resourceTypes")
        assert isinstance(result, list)
        EXPECTED_KEYS = {
            "id",
            "name",
            "nameTranslated",
            "sortKey",
            "campusId",
        }
        assert set(next(iter(result))) == EXPECTED_KEYS

    def test_get_resource_masterdata_resources(self) -> None:
        """Check resources can be retrieved."""
        result = self.api.get_resource_masterdata(resultClass="resources")
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        EXPECTED_KEYS = {
            "id",
            "name",
            "nameTranslated",
            "sortKey",
            "resourceTypeId",
            "location",
            "iCalLocation",
            "isAutoAccept",
            "doesRequireCalEntry",
            "isVirtual",
            "adminIds",
            "randomString",
        }

        assert set(result[0]) == EXPECTED_KEYS

    def test_get_resource_masterdata_resources_dict(self) -> None:
        """Check resources can be retrieved as dict."""
        result = self.api.get_resource_masterdata(
            resultClass="resources", returnAsDict=True
        )

        assert isinstance(result, dict)
        assert isinstance(next(iter(result.keys())), int)
        assert isinstance(next(iter(result.values())), dict)

        EXPECTED_KEYS = {
            "id",
            "name",
            "nameTranslated",
            "sortKey",
            "resourceTypeId",
            "location",
            "iCalLocation",
            "isAutoAccept",
            "doesRequireCalEntry",
            "isVirtual",
            "adminIds",
            "randomString",
        }

        assert set(next(iter(result.values())).keys()) == EXPECTED_KEYS

    def test_get_resource_masterdata_other(self, caplog) -> None:
        """Checks that masterdata with invalid resultclass loggs error.

        Args:
            caplog: pytest caplog instance used to caputre logging
        """
        caplog.clear()
        with caplog.at_level(level=logging.ERROR, logger="churchtools_api.resources"):
            self.api.get_resource_masterdata(resultClass=" ")
        expected_error_message = "get_resource_masterdata does not know result_type= "
        assert expected_error_message in caplog.messages

    def test_get_booking_by_id(self) -> None:
        """Checks get_booking_by_id.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        SAMPLE_BOOKING_ID = 5108
        result = self.api.get_bookings(booking_id=SAMPLE_BOOKING_ID)
        assert result[0]["id"] == SAMPLE_BOOKING_ID

    def test_get_booking_by_resource_ids(self) -> None:
        """Checks get_booking_by_resource_ids.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        RESOURCE_ID_SAMPLES = [8, 20]
        result = self.api.get_bookings(resource_ids=RESOURCE_ID_SAMPLES)
        result_resource_ids = {i["base"]["resource"]["id"] for i in result}
        assert set(RESOURCE_ID_SAMPLES) == result_resource_ids

    def test_get_booking_by_status_ids(self, caplog) -> None:
        """Checks get_booking_by_status_ids.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        STATUS_ID_SAMPLES = [2]
        with caplog.at_level(level=logging.ERROR, logger="churchtools_api.resources"):
            self.api.get_bookings(status_ids=STATUS_ID_SAMPLES)
        EXPECTED_MESSAGES = [
            "invalid argument combination in get_bookings"
            " - please check docstring for requirements"
        ]
        assert caplog.messages == EXPECTED_MESSAGES

    def test_get_booking_by_resource_and_status_ids(self) -> None:
        """Checks get_booking_by_resource_and_status_ids.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        STATUS_ID_SAMPLES = [2]
        RESOURCE_ID_SAMPLES = [8]
        result = self.api.get_bookings(
            resource_ids=RESOURCE_ID_SAMPLES,
            status_ids=STATUS_ID_SAMPLES,
        )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}
        assert set(STATUS_ID_SAMPLES) == {i["base"]["statusId"] for i in result}

    def test_get_booking_from_to_date_without_resource_id(self, caplog) -> None:
        """Checks get_booking_from_to_date_without_resource_id.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        SAMPLE_DATES = {
            "from_": datetime(year=2024, month=12, day=24).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
            "to_": datetime(year=2024, month=12, day=24).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
        }
        caplog.clear()
        with caplog.at_level(level=logging.WARNING, logger="churchtools_api.resources"):
            self.api.get_bookings(from_=SAMPLE_DATES["from_"])

        EXPECTED_MESSAGES = [
            "invalid argument combination in get_bookings"
            " - please check docstring for requirements"
        ]
        assert caplog.messages == EXPECTED_MESSAGES

    def test_get_booking_from_date(self, caplog) -> None:
        """Checks get_booking_from_date.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        RESOURCE_ID_SAMPLES = [8, 20]
        SAMPLE_DATES = {
            "from_": datetime(year=2024, month=9, day=21).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
            "to_": datetime(year=2024, month=9, day=30).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
        }
        caplog.clear()
        with caplog.at_level(logging.INFO):
            result = self.api.get_bookings(
                from_=SAMPLE_DATES["from_"],
                resource_ids=RESOURCE_ID_SAMPLES,
            )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}

        result_dates = {
            datetime.strptime(i["calculated"]["startDate"][:10], "%Y-%m-%d").astimezone(
                pytz.timezone("Europe/Berlin")
            )
            for i in result
        }
        assert all(
            SAMPLE_DATES["from_"] <= compare_date for compare_date in result_dates
        )

        EXPECTED_MESSAGES = [
            "missing from_ or to_ defaults to first or last day of current month"
        ]
        assert caplog.messages == EXPECTED_MESSAGES

    def test_get_booking_to_date(self, caplog) -> None:
        """Checks get_booking_to_date.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        RESOURCE_ID_SAMPLES = [8, 20]
        SAMPLE_DATES = {
            "to_": datetime.now().astimezone(pytz.timezone("Europe/Berlin"))
            + timedelta(days=30),
        }

        caplog.clear()
        with caplog.at_level(level=logging.INFO, logger="churchtools_api.resources"):
            result = self.api.get_bookings(
                to_=SAMPLE_DATES["to_"],
                resource_ids=RESOURCE_ID_SAMPLES,
            )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}

        result_dates = {
            datetime.strptime(i["calculated"]["startDate"][:10], "%Y-%m-%d").astimezone(
                pytz.timezone("Europe/Berlin")
            )
            for i in result
        }
        assert all(SAMPLE_DATES["to_"] >= compare_date for compare_date in result_dates)

        expected_response = (
            "missing from_ or to_ defaults to first or last day of current month"
        )
        assert expected_response in caplog.messages

    def test_get_booking_from_to_date(self, caplog) -> None:
        """Checks get_booking_from_to_date.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        RESOURCE_ID_SAMPLES = [8, 20]
        SAMPLE_DATES = {
            "from_": datetime(year=2024, month=9, day=21).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
            "to_": datetime(year=2024, month=9, day=30).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
        }

        caplog.clear()
        with caplog.at_level(level=logging.WARNING, logger="churchtools_api.resources"):
            result = self.api.get_bookings(
                from_=SAMPLE_DATES["from_"],
                to_=SAMPLE_DATES["to_"],
                resource_ids=RESOURCE_ID_SAMPLES,
            )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}

        result_dates = {
            datetime.strptime(i["calculated"]["startDate"][:10], "%Y-%m-%d").astimezone(
                pytz.timezone("Europe/Berlin")
            )
            for i in result
        }
        assert all(
            SAMPLE_DATES["from_"] <= compare_date for compare_date in result_dates
        )
        assert all(SAMPLE_DATES["to_"] >= compare_date for compare_date in result_dates)

        assert caplog.messages == []

    def test_get_booking_appointment_id(self, caplog) -> None:
        """Checks get_booking_appointment_id.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        RESOURCE_ID_SAMPLES = [16]
        SAMPLE_DATES = {
            "from_": datetime(year=2024, month=9, day=21).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
            "to_": datetime(year=2024, month=9, day=30).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
        }
        SAMPLE_APPOINTMENT_ID = 327883  # 22.9.2024 GH
        result = self.api.get_bookings(
            appointment_id=SAMPLE_APPOINTMENT_ID,
            resource_ids=RESOURCE_ID_SAMPLES,
            from_=SAMPLE_DATES["from_"],
            to_=SAMPLE_DATES["to_"],
        )

        assert result[0]["base"]["caption"] == "Zentral-Gottesdienst im Gemeindehaus"
        assert result[0]["base"]["resource"]["id"] in set(RESOURCE_ID_SAMPLES)

        caplog.clear()
        with caplog.at_level(level=logging.WARNING, logger="churchtools_api.resources"):
            result = self.api.get_bookings(
                appointment_id=SAMPLE_APPOINTMENT_ID,
                resource_ids=RESOURCE_ID_SAMPLES,
            )
        expected_log_message = (
            "using appointment ID without date range"
            " might be incomplete if current month differs"
        )
        assert expected_log_message in caplog.messages
        assert len(result) == 0

    def test_get_booking_appointment_id_daterange(self) -> None:
        """Checks get_booking_appointment_id_daterange.

        IMPORTANT - This test method and the parameters used
            depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS.
        """
        RESOURCE_ID_SAMPLES = [16]

        SAMPLE_APPOINTMENT_ID = 327883
        SAMPLE_DATES = {
            "from_": datetime(year=2024, month=9, day=22).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
            "to_": datetime(year=2024, month=9, day=22).astimezone(
                pytz.timezone("Europe/Berlin")
            ),
        }

        result = self.api.get_bookings(
            from_=SAMPLE_DATES["from_"],
            to_=SAMPLE_DATES["to_"],
            appointment_id=SAMPLE_APPOINTMENT_ID,
            resource_ids=RESOURCE_ID_SAMPLES,
        )

        result_date = datetime.strptime(
            result[0]["calculated"]["startDate"][:10],
            "%Y-%m-%d",
        ).astimezone(pytz.timezone("Europe/Berlin"))

        assert len(result) == 1
        # check dates incl. max 1 day diff because of reservations before event start
        assert SAMPLE_DATES["from_"] - timedelta(days=1) <= result_date
        assert SAMPLE_DATES["to_"] + timedelta(days=1) >= result_date
        assert result[0]["base"]["caption"] == "Zentral-Gottesdienst im Gemeindehaus"
        assert result[0]["base"]["resource"]["id"] in set(RESOURCE_ID_SAMPLES)

    def test_get_booking_problematic(self) -> None:
        """ELKW1610.krz.tools specific test case after problematic results."""
        SAMPLE_RESOURCE_IDS = [8, 20, 21, 16, 17]
        SAMPLE_DATE = datetime(2024, 11, 24, 9).astimezone(
            pytz.timezone("Europe/Berlin")
        )
        SAMPLE_APPOINTMENT_ID = 327616

        result = self.api.get_bookings(
            resource_ids=SAMPLE_RESOURCE_IDS,
            from_=SAMPLE_DATE,
            to_=SAMPLE_DATE,
            appointment_id=SAMPLE_APPOINTMENT_ID,
        )

        assert len(result) > 0
