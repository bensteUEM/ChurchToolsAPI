from setuptools import setup, find_packages

with open("README.md", "r") as file:
    description = file.read()

setup(
    name='ChurchToolsApi',
    version='1.2.1.1',
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
    package_data={
        'ChurchToolsWebService': ['templates/*.html', 'static/*']
    },
    install_requires=[
        # Add more dependencies as necessary
    ],
)