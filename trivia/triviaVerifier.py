from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaContentScanner import TriviaContentScanner
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaHistoryRepository import \
        TriviaHistoryRepository
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timberInterface import TimberInterface
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaHistoryRepository import TriviaHistoryRepository
    from trivia.triviaType import TriviaType


class TriviaVerifier():

    def __init__(
        self,
        bannedTriviaIdsRepository: BannedTriviaIdsRepositoryInterface,
        timber: TimberInterface,
        triviaContentScanner: TriviaContentScanner,
        triviaHistoryRepository: TriviaHistoryRepository
    ):
        if not isinstance(bannedTriviaIdsRepository, BannedTriviaIdsRepositoryInterface):
            raise ValueError(f'bannedTriviaIdsRepository argument is malformed: \"bannedTriviaIdsRepository\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaContentScanner, TriviaContentScanner):
            raise ValueError(f'triviaContentScanner argument is malformed: \"{triviaContentScanner}\"')
        elif not isinstance(triviaHistoryRepository, TriviaHistoryRepository):
            raise ValueError(f'triviaHistoryRepository argument is malformed: \"{triviaHistoryRepository}\"')

        self.__bannedTriviaIdsRepository: BannedTriviaIdsRepositoryInterface = bannedTriviaIdsRepository
        self.__timber: TimberInterface = timber
        self.__triviaContentScanner: TriviaContentScanner = triviaContentScanner
        self.__triviaHistoryRepository: TriviaHistoryRepository = triviaHistoryRepository

    async def checkContent(
        self,
        question: Optional[AbsTriviaQuestion],
        triviaFetchOptions: TriviaFetchOptions
    ) -> TriviaContentCode:
        if question is None:
            return TriviaContentCode.IS_NONE

        if not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        if not triviaFetchOptions.areQuestionAnswerTriviaQuestionsEnabled() and question.getTriviaType() is TriviaType.QUESTION_ANSWER:
            self.__timber.log('TriviaVerifier', f'The given TriviaType is illegal: {question.getTriviaType()} (triviaFetchOptions: {triviaFetchOptions.toStr()})')
            return TriviaContentCode.ILLEGAL_TRIVIA_TYPE
        elif triviaFetchOptions.requireQuestionAnswerTriviaQuestion() and question.getTriviaType() is not TriviaType.QUESTION_ANSWER:
            self.__timber.log('TriviaVerifier', f'The given TriviaType is illegal: {question.getTriviaType()} (triviaFetchOptions: {triviaFetchOptions.toStr()})')
            return TriviaContentCode.ILLEGAL_TRIVIA_TYPE

        if await self.__bannedTriviaIdsRepository.isBanned(
            triviaId = question.getTriviaId(),
            triviaSource = question.getTriviaSource()
        ):
            return TriviaContentCode.IS_BANNED

        contentScannerCode = await self.__triviaContentScanner.verify(question)
        if contentScannerCode is not TriviaContentCode.OK:
            return contentScannerCode

        return TriviaContentCode.OK

    async def checkHistory(
        self,
        question: AbsTriviaQuestion,
        emote: str,
        triviaFetchOptions: TriviaFetchOptions
    ) -> TriviaContentCode:
        if not isinstance(question, AbsTriviaQuestion):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif not utils.isValidStr(emote):
            raise ValueError(f'emote argument is malformed: \"{emote}\"')
        elif not isinstance(triviaFetchOptions, TriviaFetchOptions):
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        contentCode = await self.__triviaHistoryRepository.verify(
            question = question, 
            emote = emote,
            twitchChannel = triviaFetchOptions.getTwitchChannel()
        )

        if contentCode is not TriviaContentCode.OK:
            return contentCode

        return TriviaContentCode.OK
