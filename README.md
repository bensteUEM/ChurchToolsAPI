# Setup
attempting another fix without merge before

## Using project source code directly

Downloading the source code of the project by default a config.py
needs to be added in the "secure" folder for default execution.
Please be aware that this will include sensitive information and should never be shared with 3rd parties and is
therefore included in gitignore

It should look like this:

```
# COMMENT FOR WHICH USER / DATE this is -> DO NOT SHARE
ct_domain = 'https://YOUR-DOMAIN.DE'
ct_token = 'TOKEN SECRET VERY LONG RANDOM STRING'
ct_users = {'USER_EMAIL': 'USER_PASSWORD'}
```

## Using it as a module

If you want to use this code as a python module certain classes will require params similar to the config file in order
to access your system

- check the docstrings for correct usage

The latest release can be found on https://github.com/bensteUEM/ChurchToolsAPI/releases

It can be installed using
```pip install git+https://github.com/bensteUEM/ChurchToolsAPI.git@vX.X.X#egg=churchtools-api'```
replacing X.X.X by a released version number

### CT Token

CT_TOKEN can be obtained / changed using the "Berechtigungen" option of the user which should be used to access the CT
instance. It is highly recommended to setup a custom user with minimal permissions for use with this module.
However please check the log files and expect incomplete results if the user is msising permissions.

# Development use

The script was last updated using VS Code. 
Test cases (e.g. from test_ChurchToolsApi.py) are automatically run when pushed to GitHub. This ensures that basic functionality is checked against at least one environment.
The Github Repo tests against against the owners production instance in order to ensure matching data for tests.

Please be aware that some of the test cases require specific IDs to be present on the CT server which is tested against.
The respective function do have a hint like the one below in the docstring of the respective functions

```
IMPORTANT - This test method and the parameters used depend on the target system!
```

You are more than welcome to contribute additional code using respective feature branches and pull requests. New functions should always include respective test cases (that can be adjusted to the automated test system upon merge request)+

There is also a main.ipynb which can be used to quickly execute single actions without writing a seperate python project

## Compatibility

Tested against the current Churchtools APIs as of Sept 2024 (CT 3.101). More information is provided on the respective ChurchTools pages.

### REST API

https://YOUR_DOMAIN/api/

Most recent access method - should be used for anything that is accessible through this API.
Documentation of additional endpoints can be found opening the respective URL.
The module was developed to support the specific use-cases by all contributors - some endpoints might not be implemented yet!

### Legacy API

https://api.church.tools/index.html

Legacy API used by the WebUI which includes some endpoints that were not yet implemented into the REST API.
Some functions can be reverse engineered using Web-Developer Console to monitor requests.
The API is subject to change and might stop working with any future release!

It is also more time consuming than the REST api as it often queries large sets of data instead of specific items.

# License

This code is provided with a CC-BY-SA license
See https://creativecommons.org/licenses/by-sa/2.0/ for details.

In short this means - feel free to do anything with it
BUT you are required to publish any changes or additional functionality (even if you intended to add functionality for
yourself only!)

Anybody using this code is more than welcome to contribute with change requests to the original repository.

## Contributors

* benste - implemented for use at Evangelische Kirchengemeinde Baiersbronn (https://www.evang-kirche-baiersbronn.de/)
* kolibri52 - Jonathan supporting Liebenzeller Gemeinschaft Oettingen (https://lgv-oe.de/)
* fschrempf - Frieder supporting CVJM Esslingen e. V. (https://cvjm-esslingen.de)
* wengc3 - https://github.com/wengc3
