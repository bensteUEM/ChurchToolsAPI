"""helper to generate pyproject.toml using version.py."""
import importlib.util
from pathlib import Path

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
            "homepage": "https://github.com/bensteUEM/ChurchToolsAPI",
            "license": "CC-BY-SA",
            "readme": "README.md",
            "dependencies": {
                "python": "^3.10",
                "python-docx": "^0.8.11",
                "requests": "^2.31.0",
                "pytz": "^2024.2",
            },
            "group": {
                "dev": {
                    "dependencies": {
                        "poetry": "^1.6.1",
                        "tomli_w": "^1.0.0",
                        "wheel": "^0.41.2",
                        "setuptools": "^66.1.1",
                        "autopep8": "^2.0.4",
                        "pytest": "^8.3.3",
                        "pre-commit": "^3.8.0",
                        "ruff": "^0.6.9",
                        "ipykernel": "^6.29.5",
                    },
                },
            },
        },
        "ruff": {
            # Exclude a variety of commonly ignored directories.
            "exclude": [
                ".bzr",
                ".direnv",
                ".eggs",
                ".git",
                ".git-rewrite",
                ".hg",
                ".ipynb_checkpoints",
                ".mypy_cache",
                ".nox",
                ".pants.d",
                ".pyenv",
                ".pytest_cache",
                ".pytype",
                ".ruff_cache",
                ".svn",
                ".tox",
                ".venv",
                ".vscode",
                "__pypackages__",
                "_build",
                "buck-out",
                "build",
                "dist",
                "node_modules",
                "site-packages",
                "venv",
            ],
            # Same as Black.
            "line-length": 88,
            "indent-width": 4,
            # Assume Python 3.10
            "target-version": "py310",
            # Group violations by containing file.
            "output-format": "grouped",
            "lint": {
                # Enable Pyflakes (`F`) and a subset of the pycodestyle (`E`)
                # codes by default.
                "select": ["ALL"],
                "ignore": ["FIX002","COM812", "ISC001"],
                "per-file-ignores": {"tests/*.py": ["S101"]},
                # Allow fix for all enabled rules (when `--fix`) is provided.
                "fixable": ["ALL"],
                "unfixable": [],
                # Allow unused variables when underscore-prefixed.
                "dummy-variable-rgx": "^(_+|(_+[a-zA-Z0-9_]*[a-zA-Z0-9]+?))$",
                "pydocstyle": {
                    "convention": "google",
                },
            },
            "format": {
                # Like Black, use double quotes for strings.
                "quote-style": "double",
                # Like Black, indent with spaces, rather than tabs.
                "indent-style": "space",
                # Like Black, respect magic trailing commas.
                "skip-magic-trailing-comma": False,
                # Like Black, automatically detect the appropriate line ending.
                "line-ending": "auto",
                # Enable auto-formatting of code examples in docstrings.
                "docstring-code-format": False,
                # Set the line length limit used when formatting
                # code snippets in docstrings.
                "docstring-code-line-length": "dynamic",
            },
        },
    },
    "build-system": {
        "requires": ["poetry-core"],
        "build-backend": "poetry.core.masonry.api",
    },
}

with Path.open("pyproject.toml", "wb") as toml_file:
    tomli_w.dump(pyproject_toml_content, toml_file)
