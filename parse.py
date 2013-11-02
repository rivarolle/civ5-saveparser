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
    """ Parse the general game options  """

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


def extract(fileReader, xml):
    # fileReader.extract_compressed_data()
    pass

if __name__ == "__main__":
    import sys
    parse(sys.argv[1])