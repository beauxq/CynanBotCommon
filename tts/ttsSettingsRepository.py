from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.jsonReaderInterface import JsonReaderInterface
    from CynanBotCommon.tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface
except:
    import utils
    from storage.jsonReaderInterface import JsonReaderInterface
    from tts.ttsSettingsRepositoryInterface import \
        TtsSettingsRepositoryInterface


class TtsSettingsRepository(TtsSettingsRepositoryInterface):

    def __init__(self, settingsJsonReader: JsonReaderInterface):
        if not isinstance(settingsJsonReader, JsonReaderInterface):
            raise ValueError(f'settingsJsonReader argument is malformed: \"{settingsJsonReader}\"')

        self.__settingsJsonReader: JsonReaderInterface = settingsJsonReader

        self.__settingsCache: Optional[Dict[str, Any]] = None

    async def clearCaches(self):
        self.__settingsCache = None

    async def getMaximumMessageSize(self) -> int:
        jsonContents = await self.__readJson()
        return utils.getIntFromDict(jsonContents, 'maxMessageSize', fallback = 200)

    async def isTtsEnabled(self) -> bool:
        jsonContents = await self.__readJson()
        return utils.getBoolFromDict(jsonContents, 'isEnabled', fallback = False)

    async def __readJson(self) -> Dict[str, Any]:
        if self.__settingsCache is not None:
            return self.__settingsCache

        jsonContents: Optional[Dict[str, Any]] = None

        if await self.__settingsJsonReader.fileExistsAsync():
            jsonContents = await self.__settingsJsonReader.readJsonAsync()
        else:
            jsonContents = dict()

        if jsonContents is None:
            raise IOError(f'Error reading from TTS settings file: {self.__settingsJsonReader}')

        self.__settingsCache = jsonContents
        return jsonContents
