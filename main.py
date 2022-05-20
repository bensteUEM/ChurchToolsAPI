import logging

from ChurchToolsApi import ChurchToolsApi

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Started main")

    from secure.defaults import domain as domain_temp

    # Create Session
    from secure.secrets import ct_token

    api = ChurchToolsApi(domain_temp)
    api.login_ct_rest_api(ct_token)
    api.check_connection_ajax()

    # Tries to upload a file as group image for test group 103
    group = api.get_groups(103)
    api.file_upload('media/pinguin.png', "groupimage", 103)

    logging.info("finished main")
