from setuptools import setup, find_packages
from versions import VERSION

with open("README.md", "r") as file:
    description = file.read()

with open('docker/requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ChurchToolsApi',
    version=VERSION,
    author='bensteUEM',
    author_email='benedict.stein@gmail.com',
    description='A python package to make use of ChurchTools API and offer a Basic WebUI for some functions',
    long_description=description,
    long_description_content_type="text/markdown",
    url='https://github.com/bensteUEM/ChurchToolsAPI',
    license='CC-BY-SA',
    python_requires='>=3.8',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'ChurchToolsWebService': ['templates/*.html', 'static/*']
    },
    install_requires=requirements,
)