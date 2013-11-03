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
        extract(civ5Save, root)

    tree = ET.ElementTree(root)
    tree.write(filename + '.transformed.xml')


def parseBase(fileReader, xml):
    """
        Parse the general game options
        Code is definetely not optimal. We'll go thorugh a round a refactoring after mapping more information
        Refactoring 1: Remove all localization queries. This will be done on a later note.
    """


    base = ET.SubElement(xml, 'base')
    version = ET.SubElement(base , 'version')

    fileReader.skip(4) #always CIV5

    version.set('save', str(fileReader.read_int()))
    version.set('game',fileReader.read_string())
    version.set('build', fileReader.read_string())

    game = ET.SubElement(base, 'game')
    game.set('currentturn', str(fileReader.read_int()))

    fileReader.skip(1) #TODO: I'll investigate later as to what this byte hold

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

    fileReader.skip(4) #TODO: an int

    dlcs = ET.SubElement(base, 'dlcs')
    while fileReader.peek() != 0:
        fileReader.skip(16) #TODO: some binary data
        fileReader.skip(4) #TODO: seems to be always 1
        dlc = ET.SubElement(dlcs, 'dlc')
        dlc.text = fileReader.read_string()

    # Fast forward to the game options position
    fileReader.forward_string(b'GAMEOPTION')

    gameoptions = ET.SubElement(base, 'gameoptions')
    option = fileReader.read_string()

    while option.startswith('GAMEOPTION'):
        opt = ET.SubElement(gameoptions, 'option')
        opt.set('enabled', str(fileReader.read_int()))
        opt.text = option
        option = fileReader.read_string()

    #Fast Forward to the game turn time to find the victory types enabled
    fileReader.forward_string(b'TURNTIMER')
    victorytypes = ET.SubElement(base, 'victorytypes')
    fileReader.read_string()        #TURNTIME_XXX
    fileReader.read_string()        #TXT_KEY_TURN_XXX
    fileReader.read_string()        #XXX
    fileReader.skip(25)             #TODO : Bunch of int. Don't know what they do for now

    #the next 5 bytes have the 5 victory types enabled - 0/1 for disabled/enabled
    victorytypes.set('VICTORY_TIME', str(fileReader.read_byte()))
    victorytypes.set('VICTORY_SPACE_RACE', str(fileReader.read_byte()))
    victorytypes.set('VICTORY_DOMINATION', str(fileReader.read_byte()))
    victorytypes.set('VICTORY_CULTURAL', str(fileReader.read_byte()))
    victorytypes.set('VICTORY_DIPLOMATIC', str(fileReader.read_byte()))


def extract(fileReader, xml):
    # fileReader.extract_compressed_data()
    pass

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])