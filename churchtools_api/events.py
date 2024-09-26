import json
import logging
import os
from datetime import datetime, timedelta
import docx

from churchtools_api.churchtools_api_abstract import ChurchToolsApiAbstract


class ChurchToolsApiEvents(ChurchToolsApiAbstract):
    """ Part definition of ChurchToolsApi which focuses on events

    Args:
        ChurchToolsApiAbstract: template with minimum references
    """

    def __init__(self):
        super()

    def get_events(self, **kwargs) -> list[dict]:
        """
        Method to get all the events from given timespan or only the next event

        Arguments:
            kwargs: optional params to modify the search criteria

        Keyword Arguments:
            eventId (int): number of event for single event lookup

            from_ (str|datetime): used as >= with starting date in format YYYY-MM-DD - added _ to name as opposed to ct_api because of reserved keyword
            to_ (str|datetime): used as < end date in format YYYY-MM-DD ONLY allowed with from_ - added _ to name as opposed to ct_api because of reserved keyword
            canceled (bool): If true, include also canceled events
            direction (str): direction of output 'forward' or 'backward' from the date defined by parameter 'from'
            limit (int): limits the number of events - Default = 1, if all events shall be retrieved insert 'None', only applies if direction is specified
            include (str): if Parameter is set to 'eventServices', the services of the event will be included

        Returns:
            list of events
        """
        url = self.domain + '/api/events'

        headers = {
            'accept': 'application/json'
        }
        params = {"limit":50} #increases default pagination size

        if 'eventId' in kwargs.keys():
            url += '/{}'.format(kwargs['eventId'])

        else:
            if 'from_' in kwargs.keys():
                from_ = kwargs['from_']
                if isinstance(from_, datetime):
                    from_ = from_.strftime("%Y-%m-%d")
                if len(from_) == 10:
                    params['from'] = from_
            if 'to_' in kwargs.keys() and 'from_' in kwargs.keys():
                to_ = kwargs['to_']
                if isinstance(to_, datetime):
                    to_ = to_.strftime("%Y-%m-%d")
                if len(to_) == 10:
                    params['to'] = to_
            elif 'to_' in kwargs.keys():
                logging.warning(
                    'Use of to_ is only allowed together with from_')
            if 'canceled' in kwargs.keys():
                params['canceled'] = kwargs['canceled']
            if 'direction' in kwargs.keys():
                params['direction'] = kwargs['direction']
            if 'limit' in kwargs.keys() and 'direction' in kwargs.keys():
                params['limit'] = kwargs['limit']
            elif 'direction' in kwargs.keys():
                logging.warning(
                    'Use of limit is only allowed together with direction keyword')
            if 'include' in kwargs.keys():
                params['include'] = kwargs['include']

        response = self.session.get(url=url, headers=headers, params=params)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = self.combine_paginated_response_data(
                response_content, url=url, headers=headers, params=params
            )
            return [response_data] if isinstance(response_data, dict) else response_data
        else:
            logging.warning(
                "Something went wrong fetching events: {}".format(
                    response.status_code))

    def get_event_by_calendar_appointment(self, appointment_id: int,
                                          start_date: str | datetime) -> dict:
        """
        This method is a helper to retrieve an event for a specific calendar appointment
        including it's event services

        Args:
            appointment_id: _description_
            start_date: either "2023-11-26T09:00:00Z", "2023-11-26" str or datetime

        Returns:
            event dict with event servics
        """

        if not isinstance(start_date, datetime):
            formats = {'iso': '%Y-%m-%dT%H:%M:%SZ', 'date': "%Y-%m-%d"}
            for format in formats:
                try:
                    start_date = datetime.strptime(start_date, format)
                    break
                except ValueError:
                    continue

        events = self.get_events(
            from_=start_date,
            to_=start_date +
            timedelta(days=1),
            include='eventServices')

        for event in events:
            if event['appointmentId'] == appointment_id:
                return event

        logging.info(
            'no event references appointment ID %s on start %s',
            appointment_id,
            start_date)
        return None

    def get_AllEventData_ajax(self, eventId):
        """
        Reverse engineered function from legacy AJAX API which is used to get all event data for one event
        Required to read special params not yet included in REST getEvents()
        Legacy AJAX request might stop working with any future release ... CSRF-Token is required in session header
        :param eventId: number of the event to be requested
        :type eventId: int
        :return: event information
        :rtype: dict
        """
        url = self.domain + '/index.php'
        headers = {
            'accept': 'application/json'
        }
        params = {'q': 'churchservice/ajax'}
        data = {
            'id': eventId,
            'func': 'getAllEventData'
        }
        response = self.session.post(
            url=url, headers=headers, params=params, data=data)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            if len(response_content['data']) > 0:
                response_data = response_content['data'][str(eventId)]
                logging.debug("AJAX Event data {}".format(response_data))
                return response_data
            else:
                logging.info(
                    "AJAX All Event data not successful - no event found: {}".format(response.status_code))
                return None
        else:
            logging.info(
                "AJAX All Event data not successful: {}".format(
                    response.status_code))
            return None

    def get_event_services_counts_ajax(self, eventId, **kwargs):
        """
        retrieve the number of services currently set for one specific event id
        optionally get the number of services for one specific id on that event only
        :param eventId: id number of the calendar event
        :type eventId: int
        :param kwargs: keyword arguments either serviceId or service_group_id
        :key serviceId: id number of the service type to be filtered for
        :key serviceGroupId: id number of the group of services to request
        :return: dict of service types and the number of services required for this event
        :rtype: dict
        """

        event = self.get_events(eventId=eventId)[0]

        if 'serviceId' in kwargs.keys() and 'serviceGroupId' not in kwargs.keys():
            service_count = 0
            for service in event['eventServices']:
                if service['serviceId'] == kwargs['serviceId']:
                    service_count += 1
            return {kwargs['serviceId']: service_count}
        elif 'serviceId' not in kwargs.keys() and 'serviceGroupId' in kwargs.keys():
            all_services = self.get_services()
            serviceGroupServiceIds = [service['id'] for service in all_services
                                      if service['serviceGroupId'] == kwargs['serviceGroupId']]

            services = {}
            for service in event['eventServices']:
                serviceId = service['serviceId']
                if serviceId in serviceGroupServiceIds:
                    if serviceId in services.keys():
                        services[serviceId] += 1
                    else:
                        services[serviceId] = 1

            return services
        else:
            logging.warning(
                'Illegal combination of kwargs - check documentation either')

    def set_event_services_counts_ajax(
            self, eventId, serviceId, servicesCount):
        """
        update the number of services currently set for one event specific id

        :param eventId: id number of the calendar event
        :type eventId: int
        :param serviceId: id number of the service type to be filtered for
        :type serviceId: int
        :param servicesCount: number of services of the specified type to be planned
        :type servicesCount: int
        :return: successful execution
        :rtype: bool
        """

        url = self.domain + '/index.php'
        headers = {
            'accept': 'application/json'
        }
        params = {'q': 'churchservice/ajax'}

        # restore other ServiceGroup assignments required for request form data

        services = self.get_services(returnAsDict=True)
        serviceGroupId = services[serviceId]['serviceGroupId']
        servicesOfServiceGroup = self.get_event_services_counts_ajax(
            eventId, serviceGroupId=serviceGroupId)
        # set new assignment
        servicesOfServiceGroup[serviceId] = servicesCount

        # Generate form specific data
        item_id = 0
        data = {
            'id': eventId,
            'func': 'addOrRemoveServiceToEvent'
        }
        for serviceIdRow, serviceCount in servicesOfServiceGroup.items():
            data['col{}'.format(item_id)] = serviceIdRow
            if serviceCount > 0:
                data['val{}'.format(item_id)] = 'checked'
            data['count{}'.format(item_id)] = serviceCount
            item_id += 1

        response = self.session.post(
            url=url, headers=headers, params=params, data=data)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_success = response_content['status'] == 'success'

            number_match = self.get_event_services_counts_ajax(
                eventId, serviceId=serviceId)[serviceId] == servicesCount
            if number_match and response_success:
                return True
            else:
                logging.warning("Request was successful but serviceId {} not changed to count {} "
                                .format(serviceId, servicesCount))
                return False
        else:
            logging.info(
                "set_event_services_counts_ajax not successful: {}".format(
                    response.status_code))
            return False

    def get_event_admins_ajax(self, eventId):
        """
        get the admin id list of an event using legacy AJAX API
        :param eventId: number of the event to be changed
        :type eventId: int
        :return: list of admin ids
        :rtype: list
        """

        event_data = self.get_AllEventData_ajax(eventId)
        if event_data is not None:
            if 'admin' in event_data.keys():
                admin_ids = [int(id) for id in event_data['admin'].split(',')]
            else:
                admin_ids = []
            return admin_ids
        else:
            logging.info('No admins found because event not found')
            return []

    def set_event_admins_ajax(self, eventId, admin_ids):
        """
        set the admin id list of an event using legacy AJAX API
        :param eventId: number of the event to be changed
        :type eventId: int
        :param admin_ids: list of admin user ids to be set as admin for event
        :type admin_ids: list
        :return: if successful
        :rtype: bool
        """

        url = self.domain + '/index.php'
        headers = {
            'accept': 'application/json'
        }
        params = {'q': 'churchservice/ajax'}

        data = {
            'id': eventId,
            'admin': ", ".join([str(id) for id in admin_ids]),
            'func': 'updateEventInfo'
        }
        response = self.session.post(
            url=url, headers=headers, params=params, data=data)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['status'] == 'success'
            logging.debug(
                "Setting Admin IDs {} for event {} success".format(
                    admin_ids, eventId))

            return response_data
        else:
            logging.info(
                "Setting Admin IDs {} for event {} failed with : {}".format(admin_ids, eventId, response.status_code))
            return False

    def get_event_agenda(self, eventId):
        """
        Retrieve agenda for event by ID from ChurchTools
        :param eventId: number of the event
        :type eventId: int
        :return: list of event agenda items
        :rtype: list
        """
        url = self.domain + '/api/events/{}/agenda'.format(eventId)
        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()
            logging.debug("Agenda load successful {}".format(response_content))

            return response_data
        else:
            logging.info(
                "Event requested that does not have an agenda with status: {}".format(
                    response.status_code))
            return None

    def export_event_agenda(self, target_format,
                            target_path='./downloads', **kwargs):
        """
        Exports the agenda as zip file for imports in presenter-programs
        :param target_format: fileformat or name of presentation software which should be supported.
            Supported formats are 'SONG_BEAMER', 'PRO_PRESENTER6' and 'PRO_PRESENTER7'
        :param target_path: Filepath of the file which should be exported (including filename)
        :param kwargs: additional keywords as listed below
        :key eventId: event id to check for agenda id should be exported
        :key agendaId: agenda id of the agenda which should be exported
            DO NOT combine with eventId because it will be overwritten!
        :key append_arrangement: if True, the name of the arrangement will be included within the agenda caption
        :key export_Songs: if True, the songfiles will be in the folder "Songs" within the zip file
        :key with_category: has no effect when exported in target format 'SONG_BEAMER'
        :return: if successful
        :rtype: bool
        """
        if 'eventId' in kwargs.keys():
            if 'agendaId' in kwargs.keys():
                logging.warning(
                    'Invalid use of params - can not combine eventId and agendaId!')
            else:
                agenda = self.get_event_agenda(eventId=kwargs['eventId'])
                agendaId = agenda['id']
        elif 'agendaId' in kwargs.keys():
            agendaId = kwargs['agendaId']
        else:
            logging.warning('Missing event or agendaId')
            return False

        # note: target path can be either a zip-file defined before function
        # call or just a folder
        is_zip = target_path.lower().endswith('.zip')
        if not is_zip:
            folder_exists = os.path.isdir(target_path)
            # If folder doesn't exist, then create it.
            if not folder_exists:
                os.makedirs(target_path)
                logging.debug("created folder : ", target_path)

            if 'eventId' in kwargs.keys():
                new_file_name = '{}_{}.zip'.format(
                    agenda['name'], target_format)
            else:
                new_file_name = '{}_agendaId_{}.zip'.format(
                    target_format, agendaId)

            target_path = os.sep.join([target_path, new_file_name])

        url = '{}/api/agendas/{}/export'.format(self.domain, agendaId)
        # NOTE the stream=True parameter below
        params = {
            'target': target_format
        }
        json_data = {}
        # The following 3 parameter 'appendArrangement', 'exportSongs' and
        # 'withCategory' are mandatory from the churchtools API side:
        if 'append_arrangement' in kwargs.keys():
            json_data['appendArrangement'] = kwargs['append_arrangement']
        else:
            json_data['appendArrangement'] = True

        if 'export_songs' in kwargs.keys():
            json_data['exportSongs'] = kwargs['export_songs']
        else:
            json_data['exportSongs'] = True

        if 'with_category' in kwargs.keys():
            json_data['withCategory'] = kwargs['with_category']
        else:
            json_data['withCategory'] = True

        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

        response = self.session.post(
            url=url,
            params=params,
            headers=headers,
            json=json_data)
        result_ok = False
        if response.status_code == 200:
            response_content = json.loads(response.content)
            agenda_data = response_content['data'].copy()
            logging.debug("Agenda package found {}".format(response_content))
            result_ok = self.file_download_from_url(
                '{}/{}'.format(self.domain, agenda_data['url']), target_path)
            if result_ok:
                logging.debug('download finished')
        else:
            logging.warning(
                "export of event_agenda failed: {}".format(
                    response.status_code))

        return result_ok

    def get_event_agenda_docx(self, agenda, **kwargs):
        """
        Function to generate a custom docx document with the content of the event agenda from churchtools
        :param agenda: event agenda with services
        :type event: dict
        :param kwargs: optional keywords as listed
        :key serviceGroups: list of servicegroup IDs that should be included - defaults to all if not supplied
        :key excludeBeforeEvent: bool: by default pre-event parts are excluded
        :return:
        """

        if 'excludeBeforeEvent' in kwargs.keys():
            excludeBeforeEvent = kwargs['excludeBeforeEvent']
        else:
            excludeBeforeEvent = False

        logging.debug('Trying to get agenda for: ' + agenda['name'])

        document = docx.Document()
        heading = agenda['name']
        heading += '- Draft' if not agenda['isFinal'] else ''
        document.add_heading(heading)
        modifiedDate = datetime.strptime(
            agenda["meta"]['modifiedDate'],
            '%Y-%m-%dT%H:%M:%S%z')
        modifiedDate2 = modifiedDate.astimezone().strftime('%a %d.%m (%H:%M:%S)')
        document.add_paragraph(
            "Download from ChurchTools including changes until.: " +
            modifiedDate2)

        agenda_item = 0  # Position Argument from Event Agenda is weird therefore counting manually
        pre_event_last_item = True  # Event start is no item therefore look for change

        for item in agenda["items"]:
            if excludeBeforeEvent and item['isBeforeEvent']:
                continue

            if item['type'] == 'header':
                document.add_heading(item["title"], level=1)
                continue

            if pre_event_last_item:  # helper for event start heading which is not part of the ct_api
                if not item['isBeforeEvent']:
                    pre_event_last_item = False
                    document.add_heading('Eventstart', level=1)

            agenda_item += 1

            title = str(agenda_item)
            title += ' ' + item["title"]

            if item['type'] == 'song':
                title += ': ' + item['song']['title']
                # TODO #5 Word... check if fails on empty song items
                title += ' (' + item['song']['category'] + ')'

            document.add_heading(title, level=2)

            responsible_list = []
            for responsible_item in item['responsible']['persons']:
                if responsible_item['person'] is not None:
                    responsible_text = responsible_item['person']['title']
                    if not responsible_item['accepted']:
                        responsible_text += ' (Angefragt)'
                else:
                    responsible_text = '?'
                responsible_text += ' ' + responsible_item['service'] + ''
                responsible_list.append(responsible_text)

            if len(item['responsible']) > 0 and len(
                    item['responsible']['persons']) == 0:
                if len(item['responsible']['text']) > 0:
                    responsible_list.append(
                        item['responsible']['text'] + ' (Person statt Rolle in ChurchTools hinterlegt!)')

            responsible_text = ", ".join(responsible_list)
            document.add_paragraph(responsible_text)

            if item['note'] is not None and item['note'] != '':
                document.add_paragraph(item["note"])

            if len(item['serviceGroupNotes']) > 0:
                for note in item['serviceGroupNotes']:
                    if note['serviceGroupId'] in kwargs['serviceGroups'].keys() and len(
                            note['note']) > 0:
                        document.add_heading(
                            "Bemerkung für {}:"
                            .format(kwargs['serviceGroups'][note['serviceGroupId']]['name']), level=4)
                        document.add_paragraph(note['note'])

        return document

    def get_persons_with_service(self, eventId: int, serviceId: int) -> list[dict]:
        """helper function which should return the list of persons that are assigned a specific service on a specific event

        Args:
            eventId: id number from Events
            serviceId: id number from service masterdata

        Returns:
            list of persons
        """

        event = self.get_events(eventId=eventId)
        eventServices = event[0]["eventServices"]
        result = [
            service for service in eventServices if service["serviceId"] == serviceId
        ]
        return result

    def get_event_masterdata(self, **kwargs):
        """
        Function to get the Masterdata of the event module
        This information is required to map some IDs to specific items
        :param kwargs: optional keywords as listed below
        :keyword type: str with name of the masterdata type (not datatype) common types are 'absenceReasons', 'songCategories', 'services', 'serviceGroups'
        :keyword returnAsDict: if the list with one type should be returned as dict by ID
        :return: list of masterdata items, if multiple types list of lists (by type)
        :rtype: list | list[list] | dict | list[dict]
        """
        url = self.domain + '/api/event/masterdata'

        headers = {
            'accept': 'application/json'
        }
        response = self.session.get(url=url, headers=headers)

        if response.status_code == 200:
            response_content = json.loads(response.content)
            response_data = response_content['data'].copy()

            if 'type' in kwargs:
                response_data = response_data[kwargs['type']]
                if 'returnAsDict' in kwargs.keys():
                    if kwargs['returnAsDict']:
                        response_data2 = response_data.copy()
                        response_data = {
                            item['id']: item for item in response_data2}
            logging.debug(
                "Event Masterdata load successful {}".format(response_data))

            return response_data
        else:
            logging.info(
                "Event Masterdata requested failed: {}".format(
                    response.status_code))
            return None
