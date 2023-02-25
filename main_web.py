import secure.defaults
from ChurchToolsWebService import *

if __name__ == '__main__':
    app.domain = secure.defaults.domain
    app.run(debug=True)
