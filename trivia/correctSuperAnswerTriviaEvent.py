import locale
from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cuteness.cutenessResult import CutenessResult
    from CynanBotCommon.trivia.absTriviaEvent import AbsTriviaEvent
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.specialTriviaStatus import SpecialTriviaStatus
    from CynanBotCommon.trivia.toxicTriviaPunishment import \
        ToxicTriviaPunishment
    from CynanBotCommon.trivia.triviaEventType import TriviaEventType
    from CynanBotCommon.trivia.triviaScoreResult import TriviaScoreResult
except:
    import utils
    from cuteness.cutenessResult import CutenessResult
    from trivia.absTriviaEvent import AbsTriviaEvent
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.specialTriviaStatus import SpecialTriviaStatus
    from trivia.toxicTriviaPunishment import ToxicTriviaPunishment
    from trivia.triviaEventType import TriviaEventType
    from trivia.triviaScoreResult import TriviaScoreResult


class CorrectSuperAnswerTriviaEvent(AbsTriviaEvent):

    def __init__(
        self,
        triviaQuestion: AbsTriviaQuestion,
        cutenessResult: CutenessResult,
        pointsForWinning: int,
        remainingQueueSize: int,
        toxicTriviaPunishments: Optional[List[ToxicTriviaPunishment]],
        specialTriviaStatus: Optional[SpecialTriviaStatus],
        actionId: str,
        answer: str,
        emote: str,
        gameId: str,
        twitchChannel: str,
        userId: str,
        userName: str,
        triviaScoreResult: TriviaScoreResult
    ):
        super().__init__(
            actionId = actionId,
            triviaEventType = TriviaEventType.SUPER_GAME_CORRECT_ANSWER
        )

        if not isinstance(triviaQuestion, AbsTriviaQuestion):
            raise ValueError(f'triviaQuestion argument is malformed: \"{triviaQuestion}\"')
        elif not isinstance(cutenessResult, CutenessResult):
            raise ValueError(f'cutenessResult argument is malformed: \"{cutenessResult}\"')
        elif not utils.isValidInt(pointsForWinning):
            raise ValueError(f'pointsForWinning argument is malformed: \"{pointsForWinning}\"')
        elif pointsForWinning < 1 or pointsForWinning > utils.getIntMaxSafeSize():
            raise ValueError(f'pointsForWinning argument is out of bounds: {pointsForWinning}')
        elif not utils.isValidInt(remainingQueueSize):
            raise ValueError(f'remainingQueueSize argument is malformed: \"{remainingQueueSize}\"')
        elif remainingQueueSize < 0 or remainingQueueSize > utils.getIntMaxSafeSize():
            raise ValueError(f'remainingQueueSize argument is out of bounds: {remainingQueueSize}')
        elif specialTriviaStatus is not None and not isinstance(specialTriviaStatus, SpecialTriviaStatus):
            raise ValueError(f'specialTriviaStatus argument is malformed: \"{specialTriviaStatus}\"')
        elif not utils.isValidStr(answer):
            raise ValueError(f'answer argument is malformed: \"{answer}\"')
        elif not utils.isValidStr(emote):
            raise ValueError(f'emote argument is malformed: \"{emote}\"')
        elif not utils.isValidStr(gameId):
            raise ValueError(f'gameId argument is malformed: \"{gameId}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif not isinstance(triviaScoreResult, TriviaScoreResult):
            raise ValueError(f'triviaScoreResult argument is malformed: \"{triviaScoreResult}\"')

        self.__triviaQuestion: AbsTriviaQuestion = triviaQuestion
        self.__cutenessResult: CutenessResult = cutenessResult
        self.__pointsForWinning: int = pointsForWinning
        self.__remainingQueueSize: int = remainingQueueSize
        self.__toxicTriviaPunishments: Optional[List[ToxicTriviaPunishment]] = toxicTriviaPunishments
        self.__specialTriviaStatus: Optional[SpecialTriviaStatus] = specialTriviaStatus
        self.__answer: str = answer
        self.__emote: str = emote
        self.__gameId: str = gameId
        self.__twitchChannel: str = twitchChannel
        self.__userId: str = userId
        self.__userName: str = userName
        self.__triviaScoreResult: TriviaScoreResult = triviaScoreResult

    def getAnswer(self) -> str:
        return self.__answer

    def getCutenessResult(self) -> CutenessResult:
        return self.__cutenessResult

    def getEmote(self) -> str:
        return self.__emote

    def getGameId(self) -> str:
        return self.__gameId

    def getPointsForWinning(self) -> int:
        return self.__pointsForWinning

    def getPointsForWinningStr(self) -> str:
        return locale.format_string("%d", self.__pointsForWinning, grouping = True)

    def getRemainingQueueSize(self) -> int:
        return self.__remainingQueueSize

    def getRemainingQueueSizeStr(self) -> str:
        return locale.format_string("%d", self.__remainingQueueSize, grouping = True)

    def getSpecialTriviaStatus(self) -> Optional[SpecialTriviaStatus]:
        return self.__specialTriviaStatus

    def getToxicTriviaPunishments(self) -> Optional[List[ToxicTriviaPunishment]]:
        return self.__toxicTriviaPunishments

    def getTriviaQuestion(self) -> AbsTriviaQuestion:
        return self.__triviaQuestion

    def getTriviaScoreResult(self) -> TriviaScoreResult:
        return self.__triviaScoreResult

    def getTwitchChannel(self) -> str:
        return self.__twitchChannel

    def getUserId(self) -> str:
        return self.__userId

    def getUserName(self) -> str:
        return self.__userName

    def hasToxicTriviaPunishments(self) -> bool:
        return utils.hasItems(self.__toxicTriviaPunishments)

    def isShiny(self) -> bool:
        return self.__specialTriviaStatus is SpecialTriviaStatus.SHINY

    def isToxic(self) -> bool:
        return self.__specialTriviaStatus is SpecialTriviaStatus.TOXIC
