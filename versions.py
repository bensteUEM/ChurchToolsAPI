import os

VERSION = '1.2.3.7'

if __name__ == '__main__':
    os.environ['VERSION'] = VERSION
    print(f"::set-output name=VERSION::{os.environ['VERSION']}")