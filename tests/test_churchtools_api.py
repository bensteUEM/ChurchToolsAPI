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


class TestsChurchToolsApi(TestsChurchToolsApiAbstract):
    def test_login_ct_rest_api_password(self) -> None:
        """Tries to create a login with churchTools using specified username and password."""
        if self.api.session is not None:
            self.api.session.close()
        username = next(iter(self.ct_users.keys()))
        password = next(iter(self.ct_users.values()))
        self.api.login_ct_rest_api(ct_user=username, ct_password=password)
        assert self.api is not None

    def test_login_ct_rest_api_token(self) -> None:
        """Checks that Userlogin using REST is working with provided TOKEN
        :return:
        """
        if self.api.session is not None:
            self.api.session.close()
        result = self.api.login_ct_rest_api(ct_token=self.ct_token)
        assert result

        username = next(iter(self.ct_users.keys()))
        password = next(iter(self.ct_users.values()))
        if self.api.session is not None:
            self.api.session.close()
        result = self.api.login_ct_rest_api(ct_user=username, ct_password=password)
        assert result

    def test_get_ct_csrf_token(self) -> None:
        """Test checks that a CSRF token can be requested using the current API status
        :return:
        """
        token = self.api.get_ct_csrf_token()
        assert (
            len(token) > 0
        ), "Token should be more than one letter but changes each time"

    def test_check_connection_ajax(self) -> None:
        """Test checks that a connection can be established using the AJAX endpoints with current session / ct_api
        :return:
        """
        result = self.api.check_connection_ajax()
        assert result

    def test_get_options(self) -> None:
        """Checks that option fields can retrieved."""
        result = self.api.get_options()
        assert "sex" in result

    def test_get_global_permissions(self) -> None:
        """IMPORTANT - This test method and the parameters used depend on the target system!

        Checks that the global permissions for the current user can be retrieved
        and one core permission and one db permission matches the expected value.
        :return:
        """
        permissions = self.api.get_global_permissions()
        assert "churchcore" in permissions
        assert "administer settings" in permissions["churchcore"]

        assert not permissions["churchcore"]["administer settings"]
        assert not permissions["churchdb"]["view birthdaylist"]
        assert permissions["churchwiki"]["view"]
