import ast
import logging
import os
import unittest
from datetime import datetime, timedelta

from churchtools_api.churchtools_api import ChurchToolsApi


class TestsChurchToolsApi(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestsChurchToolsApi, self).__init__(*args, **kwargs)

        if 'CT_TOKEN' in os.environ:
            self.ct_token = os.environ['CT_TOKEN']
            self.ct_domain = os.environ['CT_DOMAIN']
            users_string = os.environ['CT_USERS']
            self.ct_users = ast.literal_eval(users_string)
            logging.info(
                'using connection details provided with ENV variables')
        else:
            from secure.config import ct_token
            self.ct_token = ct_token
            from secure.config import ct_domain
            self.ct_domain = ct_domain
            from secure.config import ct_users
            self.ct_users = ct_users
            logging.info(
                'using connection details provided from secrets folder')

        self.api = ChurchToolsApi(
            domain=self.ct_domain,
            ct_token=self.ct_token)
        logging.basicConfig(filename='logs/TestsChurchToolsApi.log', encoding='utf-8',
                            format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                            level=logging.DEBUG)
        logging.info("Executing Tests RUN")

    def tearDown(self):
        """
        Destroy the session after test execution to avoid resource issues
        :return:
        """
        self.api.session.close()

    def test_get_calendar(self):
        """
        Tries to retrieve a list of calendars
        """
        result = self.api.get_calendars()
        self.assertGreaterEqual(len(result), 1)
        self.assertIsInstance(result, list)
        self.assertIn('id', result[0].keys())

    def test_get_calendar_apointments(self):
        """
        Tries to retrieve calendar appointments
        IMPORTANT - This test method and the parameters used depend on the target system!
        Requires the connected test system to have a calendar mapped as ID 2 and 42 (or changed if other system)
        Calendar 2 should have 3 appointments on 19.11.2023
        One event should be appointment ID=327032
        """
        # Multiple calendars

        result = self.api.get_calendar_appointments(calendar_ids=[2, 42])
        self.assertGreaterEqual(len(result), 1)
        self.assertIsInstance(result, list)
        self.assertIn('id', result[0].keys())

        # One calendar with from date only (at least 4 appointments)
        result = self.api.get_calendar_appointments(
            calendar_ids=[2], from_='2023-11-19')
        self.assertGreater(len(result), 4)
        self.assertIsInstance(result, list)
        self.assertIn('id', result[0].keys())

        # One calendar with from and to date (exactly 4 appointments)
        result = self.api.get_calendar_appointments(
            calendar_ids=[2], from_='2023-11-19', to_='2023-11-19')
        self.assertEqual(len(result), 3)
        self.assertIsInstance(result, list)
        self.assertIn('id', result[0].keys())

        # One event in a calendar
        test_appointment_id = 327032
        result = self.api.get_calendar_appointments(
            calendar_ids=[2], appointment_id=test_appointment_id)
        self.assertEqual(len(result), 1)
        self.assertIsInstance(result, list)
        self.assertIn('id', result[0].keys())
        self.assertEqual(test_appointment_id, result[0]['id'])

    def test_get_calendar_appoints_on_seriess(self):
        """
        This test should check the behaviour of get_calendar_appointments on a series
        IMPORTANT - This test method and the parameters used depend on the target system!
        Requires the connected test system to have a calendar mapped as ID 2
        Calendar 2 should have appointment 304973 with an instance of series on 26.11.2023
        """

        # Appointment Series by ID
        result = self.api.get_calendar_appointments(
            calendar_ids=[2], appointment_id=304973)
        self.assertEqual(
            result[0]['appointment']['caption'],
            "Gottesdienst Friedrichstal")
        self.assertEqual(
            result[0]['appointment']['startDate'],
            '2023-01-08T08:00:00Z')
        self.assertEqual(
            result[0]['appointment']['endDate'],
            '2023-01-08T09:00:00Z')

        # Appointment Instance by timeframe
        result = self.api.get_calendar_appointments(
            calendar_ids=[2], from_="2023-11-26", to_="2023-11-26")
        result = [appointment for appointment in result if appointment['caption']
                  == "Gottesdienst Friedrichstal"]
        self.assertEqual(result[0]['caption'], "Gottesdienst Friedrichstal")
        self.assertEqual(result[0]['startDate'], "2023-11-26T08:00:00Z")
        self.assertEqual(result[0]['endDate'], "2023-11-26T09:00:00Z")

        # Multiple appointment Instances by timeframe

        result = self.api.get_calendar_appointments(
            calendar_ids=[2], from_="2023-11-19", to_="2023-11-26")
        result = [appointment for appointment in result if appointment['caption']
                  == "Gottesdienst Friedrichstal"]
        self.assertEqual(len(result), 2)
        self.assertEqual(result[-1]['caption'], "Gottesdienst Friedrichstal")
        self.assertEqual(result[-1]['startDate'], "2023-11-26T08:00:00Z")
        self.assertEqual(result[-1]['endDate'], "2023-11-26T09:00:00Z")
