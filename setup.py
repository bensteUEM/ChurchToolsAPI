from setuptools import setup, find_packages
from version import VERSION

with open("README.md", "r") as file:
    description = file.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='ChurchToolsApi',
    version=VERSION,
    author='bensteUEM',
    author_email='benedict.stein@gmail.com',
    description='A python package to make use of ChurchTools API',
    long_description=description,
    long_description_content_type="text/markdown",
    url='https://github.com/bensteUEM/ChurchToolsAPI',
    license='CC-BY-SA',
    python_requires='>=3.8',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
)