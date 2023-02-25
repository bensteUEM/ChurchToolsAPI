import os

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

from ChurchToolsApi import ChurchToolsApi as CTAPI

app = Flask(__name__)
app.secret_key = os.urandom(16)

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
        user = request.form['user']
        password = request.form['password']
        domain = request.form['domain']

        session['ct_api'] = CTAPI(domain, ct_user=user, ct_password=password)
        if session['ct_api'].who_am_i() is not False:
            return redirect('/main')

        error = 'Invalid Login'
        return render_template('login.html', error=error, domain=app.domain)
    else:
        return render_template('login.html', domain=app.domain)


@app.route('/main')
def main():
    user = session['ct_api'].who_am_i()
    return render_template('main.html', user=user, domain=app.domain)
