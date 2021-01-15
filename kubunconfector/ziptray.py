from zipfile import ZipFile, ZIP_BZIP2, Path as ZipPath
import json

class ZipTray():

    def __init__(self, archivePath):
        self.archive = ZipFile(archivePath, 'a', ZIP_BZIP2)

    def writeFile(self, filePath, dataDict):
        self.archive.writestr(str(filePath), json.dumps(dataDict, indent=4, sort_keys=False))
    
    def readFile(self, filePath):
        with self.archive.open(str(filePath)) as fob:
            return json.load(fob)
    
    def glob(self, pattern):
        from pathlib import PurePath
        for filePath in self.archive.filelist:
            if not filePath.is_dir() and PurePath(filePath.filename).match(pattern):
                yield filePath.filename
    
    def globAndLoad(self, pattern):
        for filePath in self.glob(pattern):
            yield filePath, self.readFile(filePath)

    def fileExists(self, filePath):
        try:
            with self.archive.open(str(filePath)) as _fob:
                pass
            return True
        except:
            return False