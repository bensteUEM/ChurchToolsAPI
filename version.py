"""helper script to define version number for automation."""

import os

VERSION = "1.7.0"
__version__ = VERSION

if __name__ == "__main__":
    os.environ["VERSION"] = VERSION
