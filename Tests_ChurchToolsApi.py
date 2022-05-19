import unittest

from ChurchToolsApi import *


class ChurchToolsApiTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ChurchToolsApiTestCase, self).__init__(*args, **kwargs)
        from secure.defaults import domain as temp_domain
        self.api = ChurchToolsApi(temp_domain)
        logging.basicConfig(filename='logs/TestSNG.log', encoding='utf-8',
                            format="%(asctime)s %(name)-10s %(levelname)-8s %(message)s",
                            level=logging.DEBUG)
        logging.info("Excecuting Tests RUN")

    def test_login_ct_ajax_api(self):
        """
        Checks that Userlogin using AJAX is working with provided credentials
        :return:
        """
        from secure.secrets import users
        result = self.api.login_ct_ajax_api('beamer_maki@evang-kirche-baiersbronn.de',
                                            users['beamer_maki@evang-kirche-baiersbronn.de'])
        self.assertTrue(result)

    def test_login_ct_rest_api(self):
        """
        Checks that Userlogin using REST is working with provided TOKEN
        :return:
        """
        result = self.api.login_ct_rest_api()
        self.assertTrue(result)

    def test_get_ct_csrf_token(self):
        raise NotImplementedError()

    def test_check_connection_ajax(self):
        raise NotImplementedError()

    def test_get_songs(self):
        raise NotImplementedError()

    def test_get_groups(self):
        raise NotImplementedError()

    def test_file_upload(self):
        raise NotImplementedError()

    def test_file_upload_replace(self):
        raise NotImplementedError()

    def test_file_delete_one_file(self):
        raise NotImplementedError()

    def test_file_delete_all_file(self):
        raise NotImplementedError()


if __name__ == '__main__':
    unittest.main()
