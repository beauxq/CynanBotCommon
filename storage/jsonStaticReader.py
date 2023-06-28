from typing import Any, Dict, Optional

try:
    from CynanBotCommon.storage.jsonReaderInterface import JsonReaderInterface
except:
    from storage.jsonReaderInterface import JsonReaderInterface


class JsonStaticReader(JsonReaderInterface):

    def __init__(self, jsonContents: Optional[Dict[Any, Any]]):
        self.__jsonContents: Optional[Dict[Any, Any]] = jsonContents
        self.__isDeleted: bool = False

    def deleteFile(self):
        self.__isDeleted = True

    async def deleteFile(self):
        self.deleteFile()

    def fileExists(self) -> bool:
        return not self.__isDeleted

    async def fileExistsAsync(self) -> bool:
        return self.fileExists()

    def readJson(self) -> Optional[Dict[Any, Any]]:
        if self.__isDeleted:
            return None
        else:
            return self.__jsonContents

    async def readJsonAsync(self) -> Optional[Dict[Any, Any]]:
        return self.readJson()
