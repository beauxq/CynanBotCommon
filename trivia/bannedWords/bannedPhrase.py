from typing import Any

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.bannedWords.absBannedWord import AbsBannedWord
    from CynanBotCommon.trivia.bannedWords.bannedWordType import BannedWordType
except:
    import utils
    from trivia.bannedWords.absBannedWord import AbsBannedWord
    from trivia.bannedWords.bannedWordType import BannedWordType


class BannedPhrase(AbsBannedWord):

    def __init__(self, phrase: str):
        if not utils.isValidStr(phrase):
            raise ValueError(f'phrase argument is malformed: \"{phrase}\"')

        self.__phrase: str = phrase.lower()

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, AbsBannedWord):
            if isinstance(other, BannedPhrase):
                return self.__phrase == other.__phrase
            else:
                return False
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def getPhrase(self) -> str:
        return self.__phrase

    def getType(self) -> BannedWordType:
        return BannedWordType.PHRASE

    def __hash__(self) -> int:
        return hash((self.__phrase, self.getType()))

    def __str__(self) -> str:
        return f'phrase=\"{self.__phrase}\", type=\"{self.getType()}\"'
