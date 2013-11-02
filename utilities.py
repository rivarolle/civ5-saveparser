import zlib

def extractPayload(filename):
    #extracts the zlib payload from the civ5 save file
    with open(filename, 'rb') as fh:
        data = fh.read()
    i = 0
    while i < len(data):
        try:
            zo = zlib.decompressobj()
            decompressedData = zo.decompress(data[i:])
            f = open(filename + str(i) + '.decompressed', 'wb')
            f.write(decompressedData)
            f.close()
            i += len(data[i:]) - len(zo.unused_data)
        except zlib.error:
            i += 1

if __name__ == "__main__":
    import sys
    extractPayload(sys.argv[1])