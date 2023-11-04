import traceback
from typing import Any, Dict, List, Optional, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.emojiHelper.emojiInfo import EmojiInfo
    from CynanBotCommon.emojiHelper.emojiRepositoryInterface import \
        EmojiRepositoryInterface
    from CynanBotCommon.storage.jsonReaderInterface import JsonReaderInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from emojiHelper.emojiInfo import EmojiInfo
    from emojiHelper.emojiRepositoryInterface import EmojiRepositoryInterface
    from storage.jsonReaderInterface import JsonReaderInterface
    from timber.timberInterface import TimberInterface


class EmojiRepository(EmojiRepositoryInterface):

    def __init__(
        self,
        emojiJsonReader: JsonReaderInterface,
        timber: TimberInterface
    ):
        if not isinstance(emojiJsonReader, JsonReaderInterface):
            raise ValueError(f'emojiJsonReader argument is malformed: \"{emojiJsonReader}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__emojiJsonReader: JsonReaderInterface = emojiJsonReader
        self.__timber: TimberInterface = timber

        self.__isLoaded: bool = False
        self.__emojiInfoData: Dict[str, Optional[EmojiInfo]] = dict()

    async def fetchEmojiInfo(self, emoji: Optional[str]) -> Optional[EmojiInfo]:
        if emoji is None:
            return None
        elif not isinstance(emoji, str):
            raise ValueError(f'emoji argument is malformed: \"{emoji}\"')
        elif not utils.isValidStr(emoji):
            return None
        else:
            return await self.__fetchEmojiInfo(emoji)

    async def __fetchEmojiInfo(self, emoji: Optional[str]) -> Optional[EmojiInfo]:
        if not utils.isValidStr(emoji):
            raise ValueError(f'emoji argument is malformed: \"{emoji}\"')

        await self.__readJson()
        return self.__emojiInfoData.get(emoji)

    async def __parseDictToEmojiInfo(
        self,
        emojiDict: Optional[Dict[str, Any]]
    ) -> Optional[EmojiInfo]:
        if not isinstance(emojiDict, Dict) or not utils.hasItems(emojiDict):
            return None

        codes: Set[str] = set()
        for code in emojiDict['code']:
            codes.add(code)

        category = utils.getStrFromDict(emojiDict, 'category')
        emoji = utils.getStrFromDict(emojiDict, 'emoji')
        name = utils.getStrFromDict(emojiDict, 'name')
        subCategory = utils.getStrFromDict(emojiDict, 'subcategory')

        return EmojiInfo(
            codes = codes,
            category = category,
            emoji = emoji,
            name = name,
            subCategory = subCategory
        )

    async def __readJson(self):
        if self.__isLoaded:
            return

        self.__isLoaded = True
        self.__timber.log('EmojiRepository', f'Reading in emoji info data...')
        jsonContents = await self.__emojiJsonReader.readJsonAsync()

        if jsonContents is None or not utils.hasItems(jsonContents):
            self.__timber.log('EmojiRepository', f'Read in no data from emojiJsonReader: \"{jsonContents}\"')
            return
        elif 'emojis' not in jsonContents:
            self.__timber.log('EmojiRepository', f'\"emojis\" field not in jsonContents!')
            return

        emojisList: Optional[List[Dict[str, Any]]] = jsonContents['emojis']

        if not isinstance(emojisList, List) or not utils.hasItems(emojisList):
            self.__timber.log('EmojiRepository', f'\"emojis\" field is either malformed or empty!')
            return

        for index, emojiDict in enumerate(emojisList):
            emojiInfo: Optional[EmojiInfo] = None
            exception: Optional[Exception] = None

            try:
                emojiInfo = await self.__parseDictToEmojiInfo(emojiDict)
            except Exception as e:
                exception = e

            if emojiInfo is None or exception is not None:
                self.__timber.log('EmojiRepository', f'Failed to read in emoji info at index {index} ({emojiDict}): {exception}', exception, traceback.format_exc())
            else:
                self.__emojiInfoData[emojiInfo.getEmoji()] = emojiInfo

        self.__timber.log('EmojiRepository', f'Finished reading in {len(self.__emojiInfoData)} emoji(s)')
