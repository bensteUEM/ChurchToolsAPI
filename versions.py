import os

VERSION = '1.2.3.9'

if __name__ == '__main__':
    os.environ['VERSION'] = VERSION
    print(f"::set-env name=VERSION::{os.environ['VERSION']}")
