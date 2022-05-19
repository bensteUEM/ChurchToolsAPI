import json
import logging

import requests


def login_ct_ajax_api():
    user = "beamer_maki@evang-kirche-baiersbronn.de"
    pswd = "$r89ZURf5MjfUK0x"

    session = requests.Session()

    login_url = domain + '/?q=login/ajax&func=login'
    data = {'email': user, 'password': pswd}
    session.post(url=login_url, data=data)
    return session


def login_ct_rest_api(login_token):
    """
    Authorization: Login<token>
    If you want to authorized a request, you need to provide a Login Token as
    Authorization header in the format {Authorization: Login<token>}
    Login Tokens are generated in "Berechtigungen" of User Settings
    :param login_token: token to be used for login into CT
    :return: session object which is authorized for further requests
    """

    session = requests.Session()
    login_url = domain + '/api/whoami'
    headers = {"Authorization": 'Login ' + login_token}
    response = session.get(url=login_url, headers=headers)

    if response.status_code == 200:
        response_content = json.loads(response.content)
        logging.info('Login Successful as {}'.format(response_content['data']['email']))
        return session
    else:
        logging.warning("Login failed with {}".format(response.content.decode()))

    return session


def get_ct_csrf_token(session):
    """
    Requests CSRF Token https://hilfe.church.tools/wiki/0/API-CSRF
    This method was created when debugging file upload but was no longer required later on
    :param session:
    :return: str token
    """
    url = domain + '/api/csrftoken'
    headers = {
        'accept': 'application/json',
    }
    response = session.get(url=url, headers=headers)
    if response.status_code == 200:
        csrf_token = json.loads(response.content)["data"]
        logging.info("CSRF Token erfolgreich abgerufen {}".format(csrf_token))
        return csrf_token
    else:
        logging.warning("CSRF Token not updated because of Response {}".format(response.content.decode()))


def check_connection_ajax(session):
    """
    Checks whether a successful connection with the given token can be initiated using the legacy AJAX API
    :param session:
    :return:
    """
    url = domain + '/?q=churchservice/ajax&func=getAllFacts'
    headers = {
        'accept': 'application/json'
    }
    response = session.post(url=url, headers=headers)
    if response.status_code == 200:
        print("Response Test Connection erfolgreich")


def get_songs(session, song_id=None):
    """ Gets list of all songs from the server
    :param session
    :param song_id: optional filter by song id
    :return JSON Response Aller Lieder aus CT
    """
    url = domain + '/api/songs'
    if song_id is not None:
        url = url + '/{}'.format(song_id)
    headers = {
        'accept': 'application/json'
    }
    response = session.get(url=url, headers=headers)
    if response.status_code == 200:
        response_content = json.loads(response.content)['data']
        logging.debug("Response successful {}".format(response_content))
        return response_content


def get_groups(session, group_id=None):
    """ Gets list of all groups
    :param session
    :param group_id: optional filter by group id
    :return dict mit allen Gruppen
    """
    url = domain + '/api/groups'
    if group_id is not None:
        url = url + '/{}'.format(group_id)
    headers = {
        'accept': 'application/json'
    }
    response = session.get(url=url, headers=headers)
    if response.status_code == 200:
        response_content = json.loads(response.content)['data']
        logging.debug("Response successful {}".format(response_content))
        return response_content


def upload_file(session, file_to_upload, domain_type='song_arrangement', domain_identifier=394):
    """
    Helper function to upload an attachment to any module of ChurchTools

    :param session: which is allready Authorized
    :param file_to_upload: open file object - e.g. open('media/pinguin.png', 'rb')
    :param domain_type:  The domain type. Currently supported are 'avatar', 'groupimage', 'logo', 'attatchments',
     'html_template', 'service', 'song_arrangement', 'importtable', 'person', 'familyavatar', 'wiki_.?'.
    :param domain_identifier: ID of the object in ChurchTools
    :return:
    """

    url = domain + '/api/files/{}/{}'.format(domain_type, domain_identifier)

    # add files as files form data with dict using 'files[]' as key and (tuple of filename and fileobject)
    files = {'files[]': (file_to_upload.name, file_to_upload)}
    response = session.post(url=url, files=files)

    """
    # Issues with HEADERS in Request module when using non standard 'files[]' key in POST Request
    # Workaround for ChurchTools - generate session with /api/whoami GET request and reuse it
    # Requests module usually automatically completes required header Params e.g. Content-Type ...
    # in case manual header e.g. for AUTH is used, headers don't auto complete
    # and server rejects messsages or data is ommited 
    # Error Code 500 is also missing in API documentation
    
    headers = {'Authorization': 'Login GEHEIM'}
    response_test = requests.post(url=url, headers=headers, files=files)
    #> this fails !
    """

    if response.status_code == 200:
        response_content = json.loads(response.content)
        logging.debug("Upload successful {}".format(response_content))
    else:
        logging.warning(response.content.decode())


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Started main")

    domain = 'https://elkw1610.krz.tools'

    # Create Session
    from secure.token import ct_token

    current_session = login_ct_rest_api(ct_token)
    check_connection_ajax(current_session)

    # Tries to upload a file to the test song with ID 394
    # song = get_songs(current_session, 394)
    file = open('media/pinguin.png', 'rb')
    upload_file(current_session, file, "song_arrangement", 394)

    # Tries to upload a file as group image for test group 103
    group = get_groups(current_session, 103)
    file = open('media/pinguin.png', 'rb')
    upload_file(current_session, file, "groupimage", 103)

    logging.info("finished main")
