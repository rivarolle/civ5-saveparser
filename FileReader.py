""" Utility class that loads a binary file and exposes binary reads """

import struct
import os
import zlib

__author__ = "Hussein Kaddoura"
__copyright__ = "Copyright 2013, Hussein Kaddoura"
__credits__ = ["Hussein Kaddoura", "MouseyPounds" ]
__license__ ="MIT"
__version__ = "0.1"
__maintainer__ = "Hussein Kaddoura"
__email__ = "hussein.nawwaf@gmail.com"
__status__="Development"

class FileReader:
    """ Some basic functionality for reading data from Binary files. """

    def __init__(self, filename):
        self.filename = filename
        if isinstance(filename, str):
            self.r = open(filename, 'rb')

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.r.close()

    def skip(self,count=1):
        self.r.seek(count, 1)

    def read_byte(self):
        """ Read a single byte as an integer value """
        t = self.r.read(1)
        if len(t) != 1:
            self.eof = True
            return 0
        return ord(t)

    def read_int(self):
        """ Read a single little endian 4 byte integer """
        # My *guess* is that they're all signed
        t = self.r.read(4)
        if len(t) != 4:
            self.eof = True
            return 0
        return struct.unpack("<i", t)[0]

    def read_ints(self, count=None, esize=1):
        """ Read count tuples of esize little endian 4 byte integers and return them in a list. If count is omitted, read it as a 4 byte integer first """
        if count is None:
            count = self.read_int()
        temp = []
        while count > 0:
            if esize > 1:
                t = []
                for i in range(esize):
                    t.append(self.read_int())
                temp.append(tuple(t))
            else:
                temp.append(self.read_int())
            count -= 1
        return temp

    def read_string(self):
        """ Read an undelimited string with the length given in the first 4 bytes """
        return self.r.read(self.read_int()).decode("utf-8", 'replace')

    def read_terminated_string(self):
        """ Read a nul-terminated string. """
        s = ""
        while True:
            c = self.r.read(1)
            if ord(c) == 0:
                return s.decode("utf-8", 'replace')
            s += c

    def read_terminated_string_list(self):
        """ Read a list of nul-terminated strings, terminated by a zero-length string. """
        l = []
        while True:
            s = self.read_terminated_string().decode("utf-8", 'replace')
            if s == "":
                return l
            l.append(s)

    def read_sized_string_list(self, size):
        """ Read a block of data with a given size, and split in null-terminated strings. """
        block = self.r.read(size)
        if block.endswith("\0"):
            block = block[:-1]
        return block.split("\0")

    def extract_compressed_data(self):
        pos = self.r.tell()
        self.r.seek(0)          #go the start of the file
        data = self.r.read()    #read all the file's data

        i = 0
        while i < len(data):
            try:
                zo = zlib.decompressobj()
                decompressedData = zo.decompress(data[i:])
                with open(self.filename + str(i) + '.decompressed', 'wb') as fh:
                    fh.write(decompressedData)
                i += len(data[i:]) - len(zo.unused_data)
            except zlib.error:
                i += 1

        self.r.seek(pos) #reset the file position

if __name__ == "__main__":
    import sys
    with FileReader(sys.argv[1]) as fr:
        fr.extract_compressed_data()

