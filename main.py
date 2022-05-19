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

    # Tries to upload a file to the test song with ID 394
    # song = get_songs(current_session, 394)

    # Tries to upload a 2 files to the test song with ID 394
    api.file_upload('media/pinguin.png', "song_arrangement", 394)
    api.file_upload('media/pinguin_shell.png', "song_arrangement", 394, 'pinguin_shell.png')

    # Adds the same file again without overwrite - should exist twice
    api.file_upload('media/pinguin.png', "song_arrangement", 394, 'pinguin.png')
    # Adds the same file again without overwrite - should only exist onces and with shell style but normal name
    api.file_upload('media/pinguin_shell.png', "song_arrangement", 394, 'pinguin.png', overwrite=True)

    # Delte all Files because of testing
    api.file_delete("song_arrangement", 394, filename_for_delete='pinguin.png')

    # Tries to upload a file as group image for test group 103
    group = api.get_groups(103)
    api.file_upload('media/pinguin.png', "groupimage", 103)

    logging.info("finished main")
