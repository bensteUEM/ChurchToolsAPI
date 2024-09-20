from abc import ABC
import logging
import os
import ast

from churchtools_api.churchtools_api import ChurchToolsApi

class TestsChurchToolsApiAbstract(ABC):
    """This is supposed to be the base configuration for PyTest test classes that require API access."""

    def setup_class(self):
        print("Setup Class")
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
