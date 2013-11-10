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

traits = { 1:"alive",
           3: "human",
           2: "dead",
}

victories = { 1: "VICTORY_TIME",
              2: "VICTORY_SPACE_RACE",
              3: "VICTORY_DOMINATION",
              4: "VICTORY_CULTURAL",
              5: "VICTORY_DIPLOMATIC",
}

def parse(filename):
    """ Parses the save file and transforms it to xml    """
    root = ET.Element("root")

    with fr.FileReader(filename) as civ5Save:
        parse_base(civ5Save, root)
        parse_compressed_payload(civ5Save, root)

    tree = ET.ElementTree(root)
    tree.write(filename + '.transformed.xml')

def parse_base(fileReader, xml):
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
    #contains the type of civilization - 03 human, 01 alive, 04 missing, 02 dead
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

    #TODO: block 30-31

    #TODO: block 32
    #contains the zlib compressed data

    civs = tuple(map(lambda civ, trait, leader:  (civ, trait, leader),civilizations,leader_traits, leaders))

    civsXml = ET.SubElement(base, 'civilizations')
    for civ in civs:
        if civ[1] != 4:
            civXml = ET.SubElement(civsXml, 'civilization')
            civXml.set('name', civ[0])
            civXml.set('trait', traits[civ[1]])
            civXml.set('leader', civ[2])

    civStatesXml = ET.SubElement(base, 'civStates')
    for civState in civStates:
        civStateXml = ET.SubElement(civStatesXml, 'civState')
        civStateXml.text = civState

    victoriesXml = ET.SubElement(base, 'victories')
    for idx, victory in enumerate(victorytypes, start=1):
        victoriesXml.set(victories[idx], str(victory))

    gameoptionsXml = ET.SubElement(base, 'gameoptions')
    for gameoption in gameoptions:
        gameoptionXml = ET.SubElement(gameoptionsXml, 'gameoption')
        gameoptionXml.set('enabled', str(gameoption[1]))
        gameoptionXml.text = gameoption[0]

def parse_compressed_payload(fileReader, xml):
    files = fileReader.extract_compressed_payloads()
    print(files)

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])