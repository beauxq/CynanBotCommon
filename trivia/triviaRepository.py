import random
from typing import Dict, List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.bongoTriviaQuestionRepository import \
        BongoTriviaQuestionRepository
    from CynanBotCommon.trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from CynanBotCommon.trivia.jServiceTriviaQuestionRepository import \
        JServiceTriviaQuestionRepository
    from CynanBotCommon.trivia.lotrTriviaQuestionsRepository import \
        LotrTriviaQuestionRepository
    from CynanBotCommon.trivia.millionaireTriviaQuestionRepository import \
        MillionaireTriviaQuestionRepository
    from CynanBotCommon.trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from CynanBotCommon.trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from CynanBotCommon.trivia.triviaContentCode import TriviaContentCode
    from CynanBotCommon.trivia.triviaExceptions import (
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException,
        TooManyTriviaFetchAttemptsException)
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
    from CynanBotCommon.trivia.triviaVerifier import TriviaVerifier
    from CynanBotCommon.trivia.willFryTriviaQuestionRepository import \
        WillFryTriviaQuestionRepository
    from CynanBotCommon.trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.jokeTriviaQuestionRepository import \
        JokeTriviaQuestionRepository
    from trivia.jServiceTriviaQuestionRepository import \
        JServiceTriviaQuestionRepository
    from trivia.lotrTriviaQuestionsRepository import \
        LotrTriviaQuestionRepository
    from trivia.millionaireTriviaQuestionRepository import \
        MillionaireTriviaQuestionRepository
    from trivia.openTriviaDatabaseTriviaQuestionRepository import \
        OpenTriviaDatabaseTriviaQuestionRepository
    from trivia.quizApiTriviaQuestionRepository import \
        QuizApiTriviaQuestionRepository
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaExceptions import (
        NoTriviaCorrectAnswersException,
        NoTriviaMultipleChoiceResponsesException,
        TooManyTriviaFetchAttemptsException)
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType
    from trivia.triviaVerifier import TriviaVerifier
    from trivia.wwtbamTriviaQuestionRepository import \
        WwtbamTriviaQuestionRepository


class TriviaRepository():

    def __init__(
        self,
        bongoTriviaQuestionRepository: BongoTriviaQuestionRepository,
        jokeTriviaQuestionRepository: JokeTriviaQuestionRepository,
        jServiceTriviaQuestionRepository: JServiceTriviaQuestionRepository,
        openTriviaDatabaseTriviaQuestionRepository: OpenTriviaDatabaseTriviaQuestionRepository,
        lotrTriviaQuestionsRepository: LotrTriviaQuestionRepository,
        millionaireTriviaQuestionRepository: MillionaireTriviaQuestionRepository,
        quizApiTriviaQuestionRepository: Optional[QuizApiTriviaQuestionRepository],
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaVerifier: TriviaVerifier,
        willFryTriviaQuestionRepository: WillFryTriviaQuestionRepository,
        wwtbamTriviaQuestionRepository: WwtbamTriviaQuestionRepository
    ):
        if bongoTriviaQuestionRepository is None:
            raise ValueError(f'bongoTriviaQuestionRepository argument is malformed: \"{bongoTriviaQuestionRepository}\"')
        elif jokeTriviaQuestionRepository is None:
            raise ValueError(f'jokeTriviaQuestionRepository argument is malformed: \"{jokeTriviaQuestionRepository}\"')
        elif jServiceTriviaQuestionRepository is None:
            raise ValueError(f'jServiceTriviaQuestionRepository argument is malformed: \"{jServiceTriviaQuestionRepository}\"')
        elif lotrTriviaQuestionsRepository is None:
            raise ValueError(f'lotrTriviaQuestionsRepository argument is malformed: \"{lotrTriviaQuestionsRepository}\"')
        elif millionaireTriviaQuestionRepository is None:
            raise ValueError(f'millionaireTriviaQuestionRepository argument is malformed: \"{millionaireTriviaQuestionRepository}\"')
        elif openTriviaDatabaseTriviaQuestionRepository is None:
            raise ValueError(f'openTriviaDatabaseTriviaQuestionRepository argument is malformed: \"{openTriviaDatabaseTriviaQuestionRepository}\"')
        elif timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')
        elif triviaVerifier is None:
            raise ValueError(f'triviaVerifier argument is malformed: \"{triviaVerifier}\"')
        elif willFryTriviaQuestionRepository is None:
            raise ValueError(f'willFryTriviaQuestionRepository argument is malformed: \"{willFryTriviaQuestionRepository}\"')
        elif wwtbamTriviaQuestionRepository is None:
            raise ValueError(f'wwtbamTriviaQuestionRepository argument is malformed: \"{wwtbamTriviaQuestionRepository}\"')

        self.__bongoTriviaQuestionRepository: AbsTriviaQuestionRepository = bongoTriviaQuestionRepository
        self.__jokeTriviaQuestionRepository: AbsTriviaQuestionRepository = jokeTriviaQuestionRepository
        self.__jServiceTriviaQuestionRepository: AbsTriviaQuestionRepository = jServiceTriviaQuestionRepository
        self.__lotrTriviaQuestionsRepository: AbsTriviaQuestionRepository = lotrTriviaQuestionsRepository
        self.__millionaireTriviaQuestionRepository: AbsTriviaQuestionRepository = millionaireTriviaQuestionRepository
        self.__openTriviaDatabaseTriviaQuestionRepository: AbsTriviaQuestionRepository = openTriviaDatabaseTriviaQuestionRepository
        self.__quizApiTriviaQuestionRepository: AbsTriviaQuestionRepository = quizApiTriviaQuestionRepository
        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__triviaVerifier: TriviaVerifier = triviaVerifier
        self.__willFryTriviaQuestionRepository: AbsTriviaQuestionRepository = willFryTriviaQuestionRepository
        self.__wwtbamTriviaQuestionRepository: AbsTriviaQuestionRepository = wwtbamTriviaQuestionRepository

    async def __chooseRandomTriviaSource(self, triviaFetchOptions: TriviaFetchOptions) -> AbsTriviaQuestionRepository:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaSourcesAndWeights: Dict[TriviaSource, int] = await self.__triviaSettingsRepository.getAvailableTriviaSourcesAndWeights()

        if not triviaFetchOptions.isJokeTriviaRepositoryEnabled() and TriviaSource.JOKE_TRIVIA_REPOSITORY in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.JOKE_TRIVIA_REPOSITORY]

        if not await self.__isQuizApiAvailable() and TriviaSource.QUIZ_API in triviaSourcesAndWeights:
            del triviaSourcesAndWeights[TriviaSource.QUIZ_API]

        if not utils.hasItems(triviaSourcesAndWeights):
            raise RuntimeError(f'There are no trivia sources available to be fetched from!')

        triviaSources: List[TriviaSource] = list()
        triviaWeights: List[int] = list()

        for triviaSource in triviaSourcesAndWeights:
            triviaSources.append(triviaSource)
            triviaWeights.append(triviaSourcesAndWeights[triviaSource])

        randomChoices = random.choices(triviaSources, triviaWeights)
        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'Trivia sources returned by random.choices() is malformed: \"{randomChoices}\"')

        index: int = 0

        while index < len(randomChoices):
            triviaSource = randomChoices[index]
            triviaQuestionRepository: AbsTriviaQuestionRepository = None

            if triviaSource is TriviaSource.BONGO:
                triviaQuestionRepository = self.__bongoTriviaQuestionRepository
            elif triviaSource is TriviaSource.JOKE_TRIVIA_REPOSITORY:
                triviaQuestionRepository = self.__jokeTriviaQuestionRepository
            elif triviaSource is TriviaSource.J_SERVICE:
                triviaQuestionRepository = self.__jServiceTriviaQuestionRepository
            elif triviaSource is TriviaSource.LORD_OF_THE_RINGS:
                triviaQuestionRepository = self.__lotrTriviaQuestionsRepository
            elif triviaSource is TriviaSource.MILLIONAIRE:
                triviaQuestionRepository = self.__millionaireTriviaQuestionRepository
            elif triviaSource is TriviaSource.OPEN_TRIVIA_DATABASE:
                triviaQuestionRepository = self.__openTriviaDatabaseTriviaQuestionRepository
            elif triviaSource is TriviaSource.QUIZ_API:
                triviaQuestionRepository = self.__quizApiTriviaQuestionRepository
            elif triviaSource is TriviaSource.WILL_FRY_TRIVIA_API:
                triviaQuestionRepository = self.__willFryTriviaQuestionRepository
            elif triviaSource is TriviaSource.WWTBAM:
                triviaQuestionRepository = self.__wwtbamTriviaQuestionRepository
            else:
                raise RuntimeError(f'Unknown TriviaSource: \"{triviaSource}\"')

            if triviaFetchOptions.requireQuestionAnswerTriviaQuestion() and TriviaType.QUESTION_ANSWER not in triviaQuestionRepository.getSupportedTriviaTypes():
                index = index + 1
                continue

            return triviaQuestionRepository

        raise RuntimeError(f'Unable to find valid AbsTriviaQuestionRepository with the given TriviaFetchOptions: {triviaFetchOptions}')

    async def fetchTrivia(self, triviaFetchOptions: TriviaFetchOptions) -> AbsTriviaQuestion:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        return await self.__fetchTrivia(triviaFetchOptions = triviaFetchOptions)

    async def __fetchTrivia(self, triviaFetchOptions: TriviaFetchOptions) -> AbsTriviaQuestion:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaQuestion: AbsTriviaQuestion = None
        retryCount: int = 0
        maxRetryCount: int = await self.__triviaSettingsRepository.getMaxRetryCount()
        attemptedTriviaSources: List[TriviaSource] = list()

        while retryCount < maxRetryCount:
            triviaQuestionRepository = await self.__chooseRandomTriviaSource(triviaFetchOptions)

            try:
                triviaQuestion = await triviaQuestionRepository.fetchTriviaQuestion(triviaFetchOptions.getTwitchChannel())
            except (NoTriviaCorrectAnswersException, NoTriviaMultipleChoiceResponsesException) as e:
                self.__timber.log('TriviaRepository', f'Failed to fetch trivia question due to malformed data: {e}')

            if await self.__verifyGoodTriviaQuestion(triviaQuestion, triviaFetchOptions):
                return triviaQuestion
            else:
                retryCount = retryCount + 1

        raise TooManyTriviaFetchAttemptsException(f'Unable to fetch trivia from {attemptedTriviaSources} after {retryCount} attempts (max attempts is {maxRetryCount})')

    async def __isQuizApiAvailable(self) -> bool:
        return self.__quizApiTriviaQuestionRepository is not None

    async def __verifyGoodTriviaQuestion(
        self,
        triviaQuestion: AbsTriviaQuestion,
        triviaFetchOptions: TriviaFetchOptions
    ) -> bool:
        if triviaFetchOptions is None:
            raise ValueError(f'triviaFetchOptions argument is malformed: \"{triviaFetchOptions}\"')

        triviaContentCode = await self.__triviaVerifier.verify(triviaQuestion, triviaFetchOptions)

        if triviaContentCode == TriviaContentCode.OK:
            return True
        else:
            self.__timber.log('TriviaRepository', f'Rejected a trivia question due to content code: {triviaContentCode}')
            return False
