from datetime import datetime, timedelta
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

class Test_churchtools_api_resources(TestsChurchToolsApiAbstract):
    def test_get_resource_masterdata_resourceTypes(self):
        """Check resourceTypes can be retrieved.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        result = self.api.get_resource_masterdata(result_type="resourceTypes")
        expected_sample = {
            "id": 1,
            "name": "Technik (MAKI)",
            "nameTranslated": "Technik (MAKI)",
            "sortKey": 11,
            "campusId": 0,
        }
        assert expected_sample in result

    def test_get_resource_masterdata_resources(self):
        """Check resources can be retrieved.

        IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS
        """
        result = self.api.get_resource_masterdata(result_type="resources")
        expected_sample = {
            "id": 8,
            "name": "Marienkirche",
            "nameTranslated": "Marienkirche",
            "sortKey": 20,
            "resourceTypeId": 4,
            "location": None,
            "iCalLocation": "Oberdorfstraße 59, 72270 Baiersbronn",
            "isAutoAccept": False,
            "doesRequireCalEntry": True,
            "isVirtual": False,
            "adminIds": None,
            "randomString": "KvPmIuWpWeOwa2FISQrQfi3yhIoEa5kG",
        }
        assert expected_sample in result

    def test_get_resource_masterdata_other(self, caplog):
        caplog.set_level(logging.ERROR)
        self.api.get_resource_masterdata(result_type="")
        expected_error_message = "get_resource_masterdata does not know result_type="
        assert expected_error_message in caplog.messages

    def test_get_booking_by_id(self):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""

        SAMPLE_BOOKING_ID = 5108
        result = self.api.get_bookings(booking_id=SAMPLE_BOOKING_ID)
        assert SAMPLE_BOOKING_ID == result[0]["id"]

    def test_get_booking_by_resource_ids(self):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        RESOURCE_ID_SAMPLES = [8, 20]
        result = self.api.get_bookings(resource_ids=RESOURCE_ID_SAMPLES)
        result_resource_ids = {i["base"]["resource"]["id"] for i in result}
        assert set(RESOURCE_ID_SAMPLES) == result_resource_ids

    def test_get_booking_by_status_ids(self, caplog):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        caplog.set_level(logging.ERROR)
        STATUS_ID_SAMPLES = [2]
        self.api.get_bookings(status_ids=STATUS_ID_SAMPLES)
        expected_response = "invalid argument combination in get_bookings - please check docstring for requirements"
        assert expected_response in caplog.messages

    def test_get_booking_by_resource_and_status_ids(self):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        STATUS_ID_SAMPLES = [2]
        RESOURCE_ID_SAMPLES = [8]
        result = self.api.get_bookings(
            resource_ids=RESOURCE_ID_SAMPLES, status_ids=STATUS_ID_SAMPLES
        )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}
        assert set(STATUS_ID_SAMPLES) == {i["base"]["statusId"] for i in result}

    def test_get_booking_from_to_date_without_resource_id(self, caplog):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        caplog.set_level(logging.WARNING)
        SAMPLE_DATES = {
            "_from": datetime(year=2024, month=12, day=24),
            "_to": datetime(year=2024, month=12, day=24),
        }
        self.api.get_bookings(_from=SAMPLE_DATES["_from"])

        expected_response = "invalid argument combination in get_bookings - please check docstring for requirements"
        assert expected_response in caplog.messages

    def test_get_booking_from_date(self, caplog):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        RESOURCE_ID_SAMPLES = [8, 20]
        SAMPLE_DATES = {
            "_from": datetime(year=2024, month=9, day=21),
            "_to": datetime(year=2024, month=9, day=30),
        }

        result = self.api.get_bookings(
            _from=SAMPLE_DATES["_from"], resource_ids=RESOURCE_ID_SAMPLES
        )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}

        result_dates = {
            datetime.strptime(i["calculated"]["startDate"][:10], "%Y-%m-%d")
            for i in result
        }
        assert all(
            [SAMPLE_DATES["_from"] <= compare_date for compare_date in result_dates]
        )

        expected_response = "See ChurchTools support ticket 130123 - might have unexpected behaviour if to and from are used standalone"
        assert expected_response in caplog.messages

    def test_get_booking_to_date(self, caplog):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        RESOURCE_ID_SAMPLES = [8, 20]
        SAMPLE_DATES = {
            "_from": datetime(year=2024, month=9, day=21),
            "_to": datetime(year=2024, month=9, day=30),
        }

        result = self.api.get_bookings(
            _to=SAMPLE_DATES["_to"], resource_ids=RESOURCE_ID_SAMPLES
        )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}

        result_dates = {
            datetime.strptime(i["calculated"]["startDate"][:10], "%Y-%m-%d")
            for i in result
        }
        assert all(
            [SAMPLE_DATES["_to"] >= compare_date for compare_date in result_dates]
        )

        expected_response = "See ChurchTools support ticket 130123 - might have unexpected behaviour if to and from are used standalone"
        assert expected_response in caplog.messages

    def test_get_booking_from_to_date(self, caplog):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        RESOURCE_ID_SAMPLES = [8, 20]
        SAMPLE_DATES = {
            "_from": datetime(year=2024, month=9, day=21),
            "_to": datetime(year=2024, month=9, day=30),
        }

        caplog.set_level(logging.WARNING)

        result = self.api.get_bookings(
            _from=SAMPLE_DATES["_from"],
            _to=SAMPLE_DATES["_to"],
            resource_ids=RESOURCE_ID_SAMPLES,
        )
        assert set(RESOURCE_ID_SAMPLES) == {i["base"]["resource"]["id"] for i in result}

        result_dates = {
            datetime.strptime(i["calculated"]["startDate"][:10], "%Y-%m-%d")
            for i in result
        }
        assert all(
            [SAMPLE_DATES["_from"] <= compare_date for compare_date in result_dates]
        )
        assert all(
            [SAMPLE_DATES["_to"] >= compare_date for compare_date in result_dates]
        )

        assert [] == caplog.messages

    def test_get_booking_appointment_id(self, caplog):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        caplog.set_level(logging.INFO)

        RESOURCE_ID_SAMPLES = [16]
        SAMPLE_APPOINTMENT_ID = 327883  # 22.9 GH
        result = self.api.get_bookings(
            appointment_id=SAMPLE_APPOINTMENT_ID, resource_ids=RESOURCE_ID_SAMPLES
        )
        expected_log_message = "Performance and stability issues - use appointment_id param together with to and from for faster results and definite time range"
        assert expected_log_message in caplog.messages
        assert len(result) == 1
        assert result[0]["base"]["caption"] == "Zentral-Gottesdienst im Gemeindehaus"
        assert result[0]["base"]["resource"]["id"] in set(RESOURCE_ID_SAMPLES)

    def test_get_booking_appointment_id_daterange(self):
        """IMPORTANT - This test method and the parameters used depend on the target system!
        the hard coded sample exists on ELKW1610.KRZ.TOOLS"""
        RESOURCE_ID_SAMPLES = [16]

        SAMPLE_APPOINTMENT_ID = 327883
        SAMPLE_DATES = {
            "_from": datetime(year=2024, month=9, day=22),
            "_to": datetime(year=2024, month=9, day=22),
        }

        result = self.api.get_bookings(
            _from=SAMPLE_DATES["_from"],
            _to=SAMPLE_DATES["_to"],
            appointment_id=SAMPLE_APPOINTMENT_ID,
            resource_ids=RESOURCE_ID_SAMPLES,
        )

        result_date = datetime.strptime(
            result[0]["calculated"]["startDate"][:10], "%Y-%m-%d"
        )

        assert len(result) == 1
        # check dates incl. max 1 day diff because of reservations before event start
        assert SAMPLE_DATES["_from"] - timedelta(days=1) <= result_date
        assert SAMPLE_DATES["_to"] + timedelta(days=1) >= result_date
        assert result[0]["base"]["caption"] == "Zentral-Gottesdienst im Gemeindehaus"
        assert result[0]["base"]["resource"]["id"] in set(RESOURCE_ID_SAMPLES)
