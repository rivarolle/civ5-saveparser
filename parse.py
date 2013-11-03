import FileReader as fr
import xml.etree.cElementTree as ET
import Database as Db

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
    """


    base = ET.SubElement(xml, 'base')
    version = ET.SubElement(base , 'version')

    fileReader.skip(4)

    version.set('save', str(fileReader.read_int()))
    version.set('game',fileReader.read_string())
    version.set('build', fileReader.read_string())

    fileReader.skip(5) #TODO: I'll investigate later as to what those bytes hold

    with Db.SqliteReader('sql/Civ5DebugDatabase.db') as core:
        civKey = core.fetchOne("select ShortDescription from Civilizations where Type = ?", (fileReader.read_string(),))
        with Db.SqliteReader('sql/Localization-Expansion - Brave New World.db') as localization:
            civilization = ET.SubElement(base, 'civilization')
            civilization.text = localization.fetchOne("select Text from LocalizedText where Tag = ? and Language = 'en_US'", (civKey[0],))[0]

        with Db.SqliteReader('sql/Localization-BaseGame.db') as baseLocalization:
            handicapKey = core.fetchOne("select Description from HandicapInfos where Type = ?",(fileReader.read_string(),))
            handicap = ET.SubElement(base, 'handicap')
            handicap.text = baseLocalization.fetchOne("select Text from LocalizedText where Tag = ? and Language = 'en_US'", (handicapKey[0],))[0]
            era = ET.SubElement(base, 'era')
            era.set('starting', baseLocalization.fetchOne("select Text from LocalizedText where Tag = ? and language='en_US'", core.fetchOne('select Description from Eras where Type = ?', (fileReader.read_string(),)))[0])
            era.set('current', baseLocalization.fetchOne("select Text from LocalizedText where Tag = ? and language='en_US'", core.fetchOne('select Description from Eras where Type = ?', (fileReader.read_string(),)))[0])
            gamespeed = ET.SubElement(base, 'gamespeed')
            gamespeed.text = baseLocalization.fetchOne("select Text from LocalizedText where Tag = ? and language='en_US'", core.fetchOne('select Description from GameSpeeds where Type = ?', (fileReader.read_string(),)))[0]
            worldsize = ET.SubElement(base, 'worldsize')
            worldsize.text = baseLocalization.fetchOne("select Text from LocalizedText where Tag = ? and language='en_US'", core.fetchOne('select Description from Worlds where Type = ?', (fileReader.read_string(),)))[0]

    mapscript = ET.SubElement(base, 'mapscript')
    mapscript.text = fileReader.read_string()

    fileReader.skip(4) #TODO: an int

    dlcs = ET.SubElement(base, 'dlcs')
    while fileReader.peek() > 0:
        fileReader.skip(16) #TODO: some binary data
        fileReader.skip(4) #TODO: seems to be always 1
        dlc = ET.SubElement(dlcs, 'dlc')
        dlc.text = fileReader.read_string()

    # Fast forward to the game options position
    fileReader.forward_string(b'GAMEOPTION')

    gameoptions = ET.SubElement(base, 'gameoptions')

    with Db.SqliteReader('sql/Civ5DebugDatabase.db') as core:
        with Db.SqliteReader('sql/Localization-BaseGame.db') as baseLocalization:
            option = fileReader.read_string()

            while option.startswith('GAMEOPTION'):
                opt = ET.SubElement(gameoptions, 'option')
                opt.set('enabled', str(fileReader.read_int()))
                opt.text = baseLocalization.fetchOne("select Text from LocalizedText where Tag = ? and language='en_US'", core.fetchOne('select Description from GameOptions where Type = ?', (option,)))[0]
                option = fileReader.read_string()

    #Fast Forward to the game turn time to find the victory types enabled
    fileReader.forward_string(b'TURNTIMER')
    victorytypes = ET.SubElement(base, 'victorytypes')
    fileReader.read_string()        #TURNTIME_XXX
    fileReader.read_string()        #TXT_KEY_TURN_XXX
    fileReader.read_string()        #XXX
    fileReader.skip(25)             #TODO : Bunch of int. Don't know what they do for now

    #the next 5 bytes have the 5 victory types enabled - 0/1 for disabled/enabled
    with Db.SqliteReader('sql/Localization-BaseGame.db') as baseLocalization:
        victorytypes.set(baseLocalization.fetchOne("select Text from LocalizedText where Tag = 'TXT_KEY_VICTORY_TIME' and language='en_US'",())[0], str(fileReader.read_byte()))
        victorytypes.set(baseLocalization.fetchOne("select Text from LocalizedText where Tag = 'TXT_KEY_VICTORY_SPACE_RACE' and language='en_US'", () )[0], str(fileReader.read_byte()))
        victorytypes.set(baseLocalization.fetchOne("select Text from LocalizedText where Tag = 'TXT_KEY_VICTORY_DOMINATION' and language='en_US'",() )[0], str(fileReader.read_byte()))
        victorytypes.set(baseLocalization.fetchOne("select Text from LocalizedText where Tag = 'TXT_KEY_VICTORY_CULTURAL' and language='en_US'",() )[0], str(fileReader.read_byte()))
        victorytypes.set(baseLocalization.fetchOne("select Text from LocalizedText where Tag = 'TXT_KEY_VICTORY_DIPLOMATIC' and language='en_US'",() )[0], str(fileReader.read_byte()))


def extract(fileReader, xml):
    # fileReader.extract_compressed_data()
    pass

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])