""" Utility class that loads a binary file and exposes binary reads """

import struct
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

    @property
    def pos(self):
        return self.bits.pos

    @pos.setter
    def pos(self, value):
        self.bits.pos = value

    def read_string(self):
        """ Read an undelimited string with the length given in the first 4 bytes """
        return self.bits.read('bytes:{0}'.format(self.read_int())).decode("utf-8", 'replace')
    #
    # def find(self, bytes, forward = True, offset = -4, searchFromCurrentPos = False):
    #     """
    #     Searches a byte object in the file.
    #     forward = True : sets the position on the first occurrence of the pattern
    #     returns position of the pattern of -1 if not found
    #     """
    #     curPos = self.r.tell()
    #     if not searchFromCurrentPos:
    #         self.r.seek(0)
    #
    #     f = Bits(self.r)
    #     occ = f.find(bytes, bytealigned=True, start=int(self.r.tell()*8))
    #
    #     if len(occ)> 0:
    #         pos = int(occ[0]/8)
    #         if forward:
    #             self.r.seek(pos + offset)
    #         else:
    #             self.r.seek(curPos)
    #
    #         return pos + offset
    #
    #     return 0 #not found
    #
    # def findall(self, bytes):
    #     f = Bits(self.r)
    #     return map(lambda x: int(x/8), f.findall(bytes))
    #
    #
    # def forward_string(self, bytes):
    #     return self.find(bytes, True)
    #
    #
    # def extract_compressed_data(self):
    #     curpos = self.r.tell()
    #     # self.r.seek(0)          #go the start of the file
    #     # data = self.r.read()    #read all the file's data
    #     # find the start of the zlib magic number 78 9C EC BD
    #
    #     i=0
    #     occ = self.findall('0x789C')
    #     for pos in occ:
    #         self.r.seek(pos)
    #
    #         #read the start of the stream into a buffer.
    #         buf = self.r.read(2**12)
    #         zo = zlib.decompressobj()
    #
    #         #start the decompression
    #         try:
    #             stream = zo.decompress(buf)
    #         except zlib.error: # right magic number but not a zlib stream.
    #             continue
    #
    #         while zo.unused_data == b'':
    #             block = self.r.read(2**12)
    #             if len(block)> 0:
    #                 try:
    #                     stream += zo.decompress(block)
    #                 except zlib.error:
    #                     pass
    #             else:
    #                 break # we've reached EOF
    #
    #         with open(self.filename + '_' + str(i) + '.decompressed', 'wb') as fh:
    #             fh.write(stream)
    #
    #         i+=1
    #
    #     self.r.seek(curpos) #reset the file position



if __name__ == "__main__":
    import sys
    with FileReader(sys.argv[1]) as fr:
        pass
        # fr.extract_compressed_data()

