import logging

from ChurchToolsApi import ChurchToolsApi


def assign_specific_tag_to_all_songs(api):
    """
    Helper to append a tag to all songs - e.g. 51 is tag:"in ChurchTools vor Skript Import"
    :param api:
    :return:
    """
    songs = api.get_songs()
    all_song_ids = [value['id'] for value in songs]
    for id in all_song_ids:
        api.add_song_tag(id, 51)


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Started main")


    # Create Session
    from secure.defaults import domain as domain_temp
    from secure.secrets import ct_token
    api = ChurchToolsApi(domain_temp)
    api.login_ct_rest_api(ct_token)

    #assign_specific_tag_to_all_songs(api)

    logging.info("finished main")
