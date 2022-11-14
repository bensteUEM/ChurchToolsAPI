# Setup

This code requires changes in 2 files within the "secure" folder in order to work

## Initial configuration

### Server connection

defaults.py with

```
domain = 'https://YOUR_DOMAIN'
```

obviously YOUR_DOMAIN needs to be replaced by the respective server to be used.
it needs to be the domain only, do not include a /api or similar.
e.g. http://churchtools.test

### Login Details

secrets.py contains the configuration for the user login used:

```
ct_token = 'CT_TOKEN'
users = {'CT_USER_NAME': 'CT_PASSWORT'}
```

CT_TOKEN can be obtained / changed using the "Berechtigungen" option of the user which should be used to access the CT
instance
It is highly recommended to setup a custom user with minimal permissions for this task!

# Usage

The script was coded using PyCharm Community edition. It is highly recomended to run the test cases successfully before use.
Please be aware that some of the test cases require specific IDs to be present on the CT server which is tested against.
The respective function do have a hint like the one below in the docstring of the respective functions
```
IMPORTANT - This test method and the parameters used depend on the target system!
```

## Compatibility

Tested against the current Churchtools APIs as of Nov 2022.
More information is provided on the respective ChurchTools pages.

### REST API

https://YOUR_DOMAIN/api/

More recent and should be used for anything that is accessible through this API.

### Legacy API

https://api.church.tools/index.html

Legacy API used by the WebUI which includes some endpoints that were not yet implemented into the REST API

# License

This code is provided with a CC-BY-SA license
See https://creativecommons.org/licenses/by-sa/2.0/ for details.

In short this means - feel free to do anything with it
BUT you are required to publish any changes or additional functionality (even if you intended to add functionality for
yourself only!)

Anybody using this code is more than welcome to contribute with change requests to the original repository.