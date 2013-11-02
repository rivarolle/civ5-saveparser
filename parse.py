
def parse(filename):
    with open(filename, 'rb') as fh:
        data = fh.read()

    #parse base information
    parseBase(data)

def parseBase(data):
    print("starting base")

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])