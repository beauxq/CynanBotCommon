try:
    from CynanBotCommon.language.languageEntry import LanguageEntry
    from CynanBotCommon.language.wordOfTheDayResponse import \
        WordOfTheDayResponse
    from CynanBotCommon.recurringActions.recurringEvent import RecurringEvent
    from CynanBotCommon.recurringActions.recurringEventType import \
        RecurringEventType
except:
    from language.languageEntry import LanguageEntry
    from language.wordOfTheDayResponse import WordOfTheDayResponse
    from recurringActions.recurringEvent import RecurringEvent
    from recurringActions.recurringEventType import RecurringEventType


class WordOfTheDayRecurringEvent(RecurringEvent):

    def __init__(
        self,
        languageEntry: LanguageEntry,
        twitchChannel: str,
        wordOfTheDayResponse: WordOfTheDayResponse
    ):
        super().__init__(twitchChannel = twitchChannel)

        if not isinstance(languageEntry, LanguageEntry):
            raise ValueError(f'languageEntry argument is malformed: \"{languageEntry}\"')
        elif not isinstance(wordOfTheDayResponse, WordOfTheDayResponse):
            raise ValueError(f'wordOfTheDayResponse argument is malformed: \"{wordOfTheDayResponse}\"')

        self.__languageEntry: LanguageEntry = languageEntry
        self.__wordOfTheDayResponse: WordOfTheDayResponse = wordOfTheDayResponse

    def getEventType(self) -> RecurringEventType:
        return RecurringEventType.WORD_OF_THE_DAY

    def getLanguageEntry(self) -> LanguageEntry:
        return self.__languageEntry

    def getWordOfTheDayResponse(self) -> WordOfTheDayResponse:
        return self.__wordOfTheDayResponse
