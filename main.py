import logging
import json
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
    api.session.headers['csrf-token']=api.get_ct_csrf_token()
    #working: api.file_upload('G:\Downloads\Absoluto guto3.sng','song_arrangement','376','Absoluto guto3.sng')
    #working: api.file_download_fromUrl('https://lgv-oe.church.tools/?q=public/filedownload&id=631&filename=738db42141baec592aa2f523169af772fd02c1d21f5acaaf0601678962d06a00','G:\ZwischenHimmelUndErde5.sng')

    api.file_download('Zwischen Himmel und Erde.sng','song_arrangement',10)

    #assign_specific_tag_to_all_songs(api)

    logging.info("finished main")
