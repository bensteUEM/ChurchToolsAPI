from ChurchToolsWebService import *

if __name__ == '__main__':
    ct_domain = os.environ.get('ct_domain')
    app.ct_domain = ct_domain
    app.run(debug=True, host='0.0.0.0')
