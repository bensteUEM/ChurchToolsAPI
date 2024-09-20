import importlib.util
import tomli_w

# Load the version number from version.py
spec = importlib.util.spec_from_file_location("version", "version.py")
version_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_module)
version = version_module.__version__

# Define the pyproject.toml content with the version
pyproject_toml_content = {
    "tool": {
        "poetry": {
            "name": "churchtools-api",
            "version": version,
            "description": "A python wrapper for use with ChurchToolsAPI",
            "authors": ["bensteUEM", "kolibri52", "fschrempf"],
            "homepage": 'https://github.com/bensteUEM/ChurchToolsAPI',
            "license": "CC-BY-SA",
            "readme": "README.md",
            "dependencies": {
                "python": "^3.8",
                "python-docx": "^0.8.11",
                "requests": "^2.31.0"
            },
            "group": {
                "dev": {
                    "dependencies": {
                        "poetry": "^1.6.1",
                        "tomli_w": "^1.0.0",
                        "wheel": "^0.41.2",
                        "setuptools": "^66.1.1",
                        "autopep8": "^2.0.4",
                        "pytest" : "^8.3.3",
                    }
                }
            }
        }
    },
    "build-system": {
        "requires": ["poetry-core"],
        "build-backend": "poetry.core.masonry.api"
    }
}

with open("pyproject.toml", "wb") as toml_file:
    tomli_w.dump(pyproject_toml_content, toml_file)
