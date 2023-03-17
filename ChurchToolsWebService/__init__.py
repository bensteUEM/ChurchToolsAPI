import logging
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, session, send_file
from flask_session import Session

from ChurchToolsApi import ChurchToolsApi as CTAPI

app = Flask(__name__)
app.secret_key = os.urandom(16)
if 'CT_DOMAIN' in os.environ.keys():
    app.ct_domain = os.environ['CT_DOMAIN']

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)


@app.route('/')
def index():
    if 'ct_api' in session:
        return redirect('/main')
    else:
        return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Request login information for CT
    :return:
    """
    if request.method == 'POST':
        user = request.form['ct_user']
        password = request.form['ct_password']
        domain = request.form['ct_domain']

        session['ct_api'] = CTAPI(domain, ct_user=user, ct_password=password)
        if session['ct_api'].who_am_i() is not False:
            return redirect('/main')

        error = 'Invalid Login'
        return render_template('login.html', error=error, ct_domain=app.ct_domain)
    else:
        return render_template('login.html', ct_domain=app.ct_domain)


@app.route('/main')
def main():
    user = session['ct_api'].who_am_i()
    return render_template('main.html', ct_user=user, ct_domain=app.ct_domain)


@app.route('/events', methods=['GET', 'POST'])
def events():
    if request.method == 'POST':
        if 'event_id' not in request.form.keys():
            redirect('/events')
        event_id = int(request.form['event_id'])
        if 'submit_docx' in request.form.keys():
            event = session['events'][event_id]
            agenda = session['event_agendas'][event_id]

            selectedServiceGroups = \
                {key: value for key, value in session['serviceGroups'].items()
                 if 'service_group {}'.format(key) in request.form}

            document = session['ct_api'].get_event_agenda_docx(agenda, serviceGroups=selectedServiceGroups,
                                                               excludeBeforeEvent=False)
            filename = agenda['name'] + '.docx'
            document.save(filename)
            response = send_file(path_or_file=os.getcwd() + '/' + filename, as_attachment=True)
            os.remove(filename)
            return response

        elif 'submit_communi' in request.form.keys():
            error = 'Communi Group update not yet implemented'
        else:
            error = 'Requested function not detected in request'
        return render_template('main.html', error=error)

    elif request.method == 'GET':
        session['serviceGroups'] = session['ct_api'].get_event_masterdata(type='serviceGroups', returnAsDict=True)

        events_temp = session['ct_api'].get_events()
        events_temp.extend(session['ct_api'].get_events(eventId=2147))  # debugging
        events_temp.extend(session['ct_api'].get_events(eventId=2129))  # debugging
        logging.debug("{} Events loaded".format(len(events_temp)))

        event_choices = []
        session['event_agendas'] = {}
        session['events'] = {}

        for event in events_temp:
            agenda = session['ct_api'].get_event_agenda(event['id'])
            if agenda is not None:
                session['event_agendas'][event['id']] = agenda
                session['events'][event['id']] = event
                startdate = datetime.fromisoformat(event['startDate'][:-1])
                datetext = startdate.astimezone().strftime('%a %b %d\t%H:%M')
                event = {'id': event['id'], 'label': datetext + '\t' + event['name']}
                event_choices.append(event)

        logging.debug("{} Events kept because schedule exists".format(len(events_temp)))

        return render_template('events.html', ct_domain=app.ct_domain, event_choices=event_choices,
                               service_groups=session['serviceGroups'])
