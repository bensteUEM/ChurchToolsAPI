import secure.config
from ChurchToolsWebService import *

if __name__ == '__main__':
    app.ct_domain = secure.config.ct_domain
    app.run(debug=True)
