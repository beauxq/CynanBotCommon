from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.startNewTriviaGameAction import \
        StartNewTriviaGameAction
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaGameBuilderInterface import \
        TriviaGameBuilderInterface
    from CynanBotCommon.trivia.triviaGameBuilderSettingsInterface import \
        TriviaGameBuilderSettingsInterface
    from CynanBotCommon.users.usersRepositoryInterface import \
        UsersRepositoryInterface
except:
    import utils
    from trivia.questionAnswerTriviaConditions import \
        QuestionAnswerTriviaConditions
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.startNewTriviaGameAction import StartNewTriviaGameAction
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaGameBuilderInterface import TriviaGameBuilderInterface
    from trivia.triviaGameBuilderSettingsInterface import \
        TriviaGameBuilderSettingsInterface

    from users.usersRepositoryInterface import UsersRepositoryInterface


class TriviaGameBuilder(TriviaGameBuilderInterface):

    def __init__(
        self,
        triviaGameBuilderSettings: TriviaGameBuilderSettingsInterface,
        usersRepository: UsersRepositoryInterface
    ):
        if not isinstance(triviaGameBuilderSettings, TriviaGameBuilderSettingsInterface):
            raise ValueError(f'triviaGameBuilderSettings argument is malformed: \"{triviaGameBuilderSettings}\"')
        if not isinstance(usersRepository, UsersRepositoryInterface):
            raise ValueError(f'usersRepository argument is malformed: \"{usersRepository}\"')

        self.__triviaGameBuilderSettings: TriviaGameBuilderSettingsInterface = triviaGameBuilderSettings
        self.__usersRepository: UsersRepositoryInterface = usersRepository

    async def createNewTriviaGame(
        self,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> Optional[StartNewTriviaGameAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        if not await self.__triviaGameBuilderSettings.isTriviaGameEnabled():
            return None

        user = await self.__usersRepository.getUserAsync(twitchChannel)

        if not user.isTriviaGameEnabled():
            return None

        points = await self.__triviaGameBuilderSettings.getTriviaGamePoints()
        if user.hasTriviaGamePoints():
            points = user.getTriviaGamePoints()

        secondsToLive = await self.__triviaGameBuilderSettings.getWaitForTriviaAnswerDelay()
        if user.hasWaitForTriviaAnswerDelay():
            secondsToLive = user.getWaitForTriviaAnswerDelay()

        shinyMultiplier = await self.__triviaGameBuilderSettings.getTriviaGameShinyMultiplier()
        if user.hasTriviaGameShinyMultiplier():
            shinyMultiplier = user.getTriviaGameShinyMultiplier()

        triviaFetchOptions = TriviaFetchOptions(
            twitchChannel = user.getHandle(),
            isJokeTriviaRepositoryEnabled = user.isJokeTriviaRepositoryEnabled(),
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.NOT_ALLOWED
        )

        return StartNewTriviaGameAction(
            isShinyTriviaEnabled = user.isShinyTriviaEnabled(),
            pointsForWinning = points,
            secondsToLive = secondsToLive,
            shinyMultiplier = shinyMultiplier,
            twitchChannel = user.getHandle(),
            userId = userId,
            userName = userName,
            triviaFetchOptions = triviaFetchOptions
        )

    async def createNewSuperTriviaGame(
        self,
        twitchChannel: str,
        numberOfGames: int = 1
    ) -> Optional[StartNewSuperTriviaGameAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidInt(numberOfGames):
            raise ValueError(f'numberOfGames argument is malformed: \"{numberOfGames}\"')
        elif numberOfGames < 1 or numberOfGames > utils.getIntMaxSafeSize():
            raise ValueError(f'numberOfGames argument is out of bounds: {numberOfGames}')

        if not await self.__triviaGameBuilderSettings.isSuperTriviaGameEnabled():
            return None

        user = await self.__usersRepository.getUserAsync(twitchChannel)

        if not user.isSuperTriviaGameEnabled():
            return None

        perUserAttempts = await self.__triviaGameBuilderSettings.getSuperTriviaGamePerUserAttempts()
        if user.hasSuperTriviaPerUserAttempts():
            perUserAttempts = user.getSuperTriviaPerUserAttempts()

        points = await self.__triviaGameBuilderSettings.getSuperTriviaGamePoints()
        if user.hasSuperTriviaGamePoints():
            points = user.getSuperTriviaGamePoints()

        regularTriviaPointsForWinning = await self.__triviaGameBuilderSettings.getTriviaGamePoints()
        if user.hasTriviaGamePoints():
            regularTriviaPointsForWinning = user.getTriviaGamePoints()

        secondsToLive = await self.__triviaGameBuilderSettings.getWaitForSuperTriviaAnswerDelay()
        if user.hasWaitForSuperTriviaAnswerDelay():
            secondsToLive = user.getWaitForSuperTriviaAnswerDelay()

        shinyMultiplier = await self.__triviaGameBuilderSettings.getSuperTriviaGameShinyMultiplier()
        if user.hasSuperTriviaGameShinyMultiplier():
            shinyMultiplier = user.getSuperTriviaGameShinyMultiplier()

        toxicMultiplier = await self.__triviaGameBuilderSettings.getSuperTriviaGameToxicMultiplier()
        if user.hasSuperTriviaGameToxicMultiplier():
            toxicMultiplier = user.getSuperTriviaGameToxicMultiplier()

        toxicTriviaPunishmentMultiplier = await self.__triviaGameBuilderSettings.getSuperTriviaGameToxicPunishmentMultiplier()
        if user.hasSuperTriviaGameToxicPunishmentMultiplier():
            toxicTriviaPunishmentMultiplier = user.getSuperTriviaGameToxicPunishmentMultiplier()

        triviaFetchOptions = TriviaFetchOptions(
            twitchChannel = user.getHandle(),
            isJokeTriviaRepositoryEnabled = False,
            questionAnswerTriviaConditions = QuestionAnswerTriviaConditions.REQUIRED
        )

        return StartNewSuperTriviaGameAction(
            isQueueActionConsumed = False,
            isShinyTriviaEnabled = user.isShinyTriviaEnabled(),
            isToxicTriviaEnabled = user.isToxicTriviaEnabled(),
            numberOfGames = numberOfGames,
            perUserAttempts = perUserAttempts,
            pointsForWinning = points,
            regularTriviaPointsForWinning = regularTriviaPointsForWinning,
            secondsToLive = secondsToLive,
            shinyMultiplier = shinyMultiplier,
            toxicMultiplier = toxicMultiplier,
            toxicTriviaPunishmentMultiplier = toxicTriviaPunishmentMultiplier,
            twitchChannel = user.getHandle(),
            triviaFetchOptions = triviaFetchOptions
        )
