import FileReader as fr
import xml.etree.cElementTree as ET

__author__ = "Hussein Kaddoura"
__copyright__ = "Copyright 2013, Hussein Kaddoura"
__credits__ = ["Hussein Kaddoura"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Hussein Kaddoura"
__email__ = "hussein.nawwaf@gmail.com"
__status__ = "Development"


def parse(filename):
    """ Parses the save file and transforms it to xml    """
    root = ET.Element("root")

    with fr.FileReader(filename) as civ5Save:
        parseBase(civ5Save, root)
        # extract(civ5Save, root)

    tree = ET.ElementTree(root)
    tree.write(filename + '.transformed.xml')

def parseBase(fileReader, xml):
    """
        Parse the general game options
        Code is definitely not optimal. We'll go through a round a refactoring after mapping more information
        Refactoring 1: Remove all localization queries. This will be done on a later note.
    """

    base = ET.SubElement(xml, 'base')
    version = ET.SubElement(base , 'version')

    fileReader.skip_bytes(4) #always CIV5

    version.set('save', str(fileReader.read_int()))
    version.set('game',fileReader.read_string())
    version.set('build', fileReader.read_string())

    game = ET.SubElement(base, 'game')
    game.set('currentturn', str(fileReader.read_int()))

    fileReader.skip_bytes(1) #TODO: I'll investigate later as to what this byte hold

    civilization = ET.SubElement(base, 'civilization')
    civilization.text = fileReader.read_string()

    handicap = ET.SubElement(base, 'handicap')
    handicap.text = fileReader.read_string()

    era = ET.SubElement(base, 'era')
    era.set('starting', fileReader.read_string())
    era.set('current', fileReader.read_string())

    gamespeed = ET.SubElement(base, 'gamespeed')
    gamespeed.text = fileReader.read_string()

    worldsize = ET.SubElement(base, 'worldsize')
    worldsize.text = fileReader.read_string()

    mapscript = ET.SubElement(base, 'mapscript')
    mapscript.text = fileReader.read_string()

    fileReader.skip_bytes(4) #TODO: an int
    #
    dlcs = ET.SubElement(base, 'dlcs')
    while fileReader.peek_int() != 0:
        fileReader.skip_bytes(16) #TODO: some binary data
        fileReader.skip_bytes(4) #TODO: seems to be always 1
        dlc = ET.SubElement(dlcs, 'dlc')
        dlc.text = fileReader.read_string()
    #
    # #Extract block position (separated by \x40\x00\x00\x00 (@) )
    # #I haven't decoded what each of these blocks mean but I'll extract their position for the time being.

    bit_block_position = tuple(fileReader.findall('0x40000000'))
    #32 blocks have been found. We'll try to map them one at a time.

    #block 1
    fileReader.pos = bit_block_position[0] + 32 #remove the delimiter (@)
    block1 = tuple(map(lambda x: x.read(32).intle, fileReader.read_bytes(152).cut(32)))

    #TODO: block2 - seems to only contain Player 1?

    #block3
    #contains the type of civilization - 03 human, 01 alive, 04 dead, 02 missing
    fileReader.pos = bit_block_position[2] + 32
    leader_traits = tuple(map(lambda x: x.read(32).intle, fileReader.read_bytes(256).cut(32)))

    #TODO: block4
    #TODO: block5
    #TODO: block6

    #block 7
    # contains the list of civilizations
    civilizations = fileReader.read_strings_from_block(bit_block_position[6] + 32, bit_block_position[7])

    #block 8
    #contains the list of leaders
    leaders = fileReader.read_strings_from_block(bit_block_position[7] + 32, bit_block_position[8], True)

    #TODO: block9-18

    #block 19
    # contains the civ states. There seems to be a whole bunch of leading 0s.
    fileReader.forward_to_first_non_zero_byte(bit_block_position[18] + 32, bit_block_position[19])
    civStates = fileReader.read_strings_from_block(fileReader.pos, bit_block_position[19], True)

    #TODO: block 20 - there's a 16 byte long list of 01's
    #TODO: block 21 - seems to be FFs
    #TODO: block 22, 23 - 00s
    #TODO: block 24 - player colors
    #TODO: blocks 25-27

    #block 28
    #the last 5 bytes contain the enabled victory types
    fileReader.pos = bit_block_position[28] - 5*8
    victorytypes = (fileReader.read_byte(), fileReader.read_byte(), fileReader.read_byte(), fileReader.read_byte(), fileReader.read_byte() )

    #block 29
    # have the game options
    fileReader.find(b'GAMEOPTION', bit_block_position[28]+32, bit_block_position[29])
    fileReader.pos -= 32
    gameoptions = []
    while fileReader.pos < bit_block_position[29]:
        s = fileReader.read_string()
        if s == "":
            break
        state = fileReader.read_int()
        gameoptions.append((s, state))

    #block 30-31
    #block 32
    #contains the zlib compressed data

    #
    # # Fast forward to the game options position
    # fileReader.forward_string(b'GAMEOPTION')
    #
    # gameoptions = ET.SubElement(base, 'gameoptions')
    # option = fileReader.read_string()
    #
    # while option.startswith('GAMEOPTION'):
    #     opt = ET.SubElement(gameoptions, 'option')
    #     opt.set('enabled', str(fileReader.read_int()))
    #     opt.text = option
    #     option = fileReader.read_string()
    #
    # #Fast Forward to the game turn time to find the victory types enabled
    # fileReader.forward_string(b'TURNTIMER')
    # victorytypes = ET.SubElement(base, 'victorytypes')
    # fileReader.read_string()        #TURNTIME_XXX
    # fileReader.read_string()        #TXT_KEY_TURN_XXX
    # fileReader.read_string()        #XXX
    # fileReader.skip(25)             #TODO : Bunch of int. Don't know what they do for now
    #
    # #the next 5 bytes have the 5 victory types enabled - 0/1 for disabled/enabled
    # victorytypes.set('VICTORY_TIME', str(fileReader.read_byte()))
    # victorytypes.set('VICTORY_SPACE_RACE', str(fileReader.read_byte()))
    # victorytypes.set('VICTORY_DOMINATION', str(fileReader.read_byte()))
    # victorytypes.set('VICTORY_CULTURAL', str(fileReader.read_byte()))
    # victorytypes.set('VICTORY_DIPLOMATIC', str(fileReader.read_byte()))


# def extract(fileReader, xml):
#     # fileReader.extract_compressed_data()
#     pass

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])