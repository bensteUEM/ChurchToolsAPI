import secure.config
from ChurchToolsWebService import *

if __name__ == '__main__':
    """
    Running works better when CT_DOMAIN env variable exists
    """
    app.run(debug=True)
