""" Utility class that loads a binary file and exposes binary reads """

import struct
import zlib
from bitstring import Bits

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

    def peek(self):
        curPos = self.r.tell() #save current position
        val = self.read_int()
        self.r.seek(curPos) #reset position
        return val

    def find(self, bytes, forward = True, offset = -4, searchFromCurrentPos = False):
        """
        Searches a byte object in the file.
        forward = True : sets the position on the first occurrence of the pattern
        returns position of the pattern of -1 if not found
        """
        curPos = self.r.tell()
        if not searchFromCurrentPos:
            self.r.seek(0)

        f = Bits(self.r)
        occ = f.find(bytes, bytealigned=True, start=int(self.r.tell()*8))

        if len(occ)> 0:
            pos = int(occ[0]/8)
            if forward:
                self.r.seek(pos + offset)
            else:
                self.r.seek(curPos)

            return pos + offset

        return 0 #not found

    def findall(self, bytes):
        f = Bits(self.r)
        return map(lambda x: int(x/8), f.findall(bytes))


    def forward_string(self, bytes):
        return self.find(bytes, True)


    def extract_compressed_data(self):
        curpos = self.r.tell()
        # self.r.seek(0)          #go the start of the file
        # data = self.r.read()    #read all the file's data
        # find the start of the zlib magic number 78 9C EC BD

        i=0
        occ = self.findall('0x789C')
        for pos in occ:
            self.r.seek(pos)

            #read the start of the stream into a buffer.
            buf = self.r.read(2**12)
            zo = zlib.decompressobj()

            #start the decompression
            try:
                stream = zo.decompress(buf)
            except zlib.error: # right magic number but not a zlib stream.
                continue

            while zo.unused_data == b'':
                block = self.r.read(2**12)
                if len(block)> 0:
                    try:
                        stream += zo.decompress(block)
                    except zlib.error:
                        pass
                else:
                    break # we've reached EOF

            with open(self.filename + '_' + str(i) + '.decompressed', 'wb') as fh:
                fh.write(stream)

            i+=1

        self.r.seek(curpos) #reset the file position

if __name__ == "__main__":
    import sys
    with FileReader(sys.argv[1]) as fr:
        fr.extract_compressed_data()

