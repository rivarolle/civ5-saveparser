import FileReader

__author__ = "Hussein Kaddoura"
__copyright__ = "Copyright 2013, Hussein Kaddoura"
__credits__ = ["Hussein Kaddoura"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Hussein Kaddoura"
__email__ = "hussein.nawwaf@gmail.com"
__status__ = "Development"


def parse(filename):
    with FileReader.FileReader(filename) as civ5Save:
        civ5Save.extract_compressed_data()


if __name__ == "__main__":
    import sys

    parse(sys.argv[1])