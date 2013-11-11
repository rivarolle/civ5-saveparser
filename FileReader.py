""" Utility class that loads a binary file and exposes binary reads """

import zlib
from bitstring import Bits, ConstBitStream

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
            self.file = open(filename, 'rb')
            self.bits = ConstBitStream(open(filename, 'rb'))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()

    def skip_bytes(self,count=1):
        self.bits.read('pad:{0}'.format(count*8))

    def peek_int(self):
        return self.bits.peek(32).uintle

    def forward_to_first_non_zero_byte(self, start, end):
        self.bits.pos = start
        while self.bits.pos < end and self.bits.read(8).intle == 0:
            pass
        self.bits.pos -= 8

    def read_strings_from_block(self, start, end, stopAtEmptyString=False):
        self.bits.pos = start
        r = []
        while self.bits.pos < end:
            s = self.read_string()
            if s == "" and stopAtEmptyString:
                return r
            r.append(s)
        return tuple(r)

    def read_int(self):
        """ Read a single little endian 4 byte integer """
        return self.bits.read(32).intle

    def findall(self,bs):
        return self.bits.findall(bs,bytealigned=True)

    def read_bytes(self, count):
        return self.bits.read(count*8)

    def read_byte(self):
        return self.bits.read(8).uint

    def find(self, bs, start, end):
        return self.bits.find(bs,start, end, True )

    def find_first(self, bs):
        return self.bits.find(bs)

    def extract_compressed_payloads(self):
        files = []
        occ = self.findall('0x789C')

        i = 0
        readSize = 2**12

        for pos in occ:
            self.bits.pos = pos

            #read the start of the stream into a buffer.
            if (self.bits.length - self.pos) < 8*2**12:
                readSize = int((self.bits.length - self.pos) / 8)

            buf = self.bits.read('bytes:{0}'.format(readSize))
            zo = zlib.decompressobj()

            #start the decompression
            try:
                stream = zo.decompress(buf)
            except zlib.error: # right magic number but not a zlib stream.
                continue

            while zo.unused_data == b'' and readSize >= 2**12:
                if (self.bits.length - self.pos) < 8*2**12:
                    readSize = int((self.bits.length - self.pos) / 8)

                block = self.bits.read('bytes:{0}'.format(readSize))
                if len(block)> 0:
                    try:
                        stream += zo.decompress(block)
                    except zlib.error:
                        pass
                else:
                    break # we've reached EOF

            with open(self.filename + '_' + str(i) + '.decompressed', 'wb') as fh:
                fh.write(stream)

            files.append(self.filename + '_' + str(i) + '.decompressed')

            i+=1

        return files

    @property
    def pos(self):
        return self.bits.pos

    @pos.setter
    def pos(self, value):
        self.bits.pos = value

    def read_string(self):
        """ Read an undelimited string with the length given in the first 4 bytes """
        return self.bits.read('bytes:{0}'.format(self.read_int())).decode("utf-8", 'replace')

if __name__ == "__main__":
    import sys
    with FileReader(sys.argv[1]) as fr:
        fr.extract_compressed_payloads()

