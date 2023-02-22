from flask import Flask, render_template, request, redirect

from ChurchToolsAPI.ChurchToolsApi import ChurchToolsApi as CTAPI
from secure.defaults import domain

app = Flask(__name__)


@app.route('/')
def index():
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

        app.ct_api = CTAPI(domain, ct_user=user, ct_password=password)
        if app.ct_api.who_am_i() is not False:
            return redirect('/main')

        error = 'Invalid Login'
        return render_template('login.html', error=error)
    else:
        return render_template('login.html')


@app.route('/main')
def main():
    user = app.ct_api.who_am_i()
    return render_template('main.html', user=user, domain=domain)


if __name__ == '__main__':
    app.run()
