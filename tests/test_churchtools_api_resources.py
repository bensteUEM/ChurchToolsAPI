import logging
import pytest
from tests.test_churchtools_api_abstract import TestsChurchToolsApiAbstract


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
