import queue
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, List, Set

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.addQueuedGamesResult import AddQueuedGamesResult
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
except:
    import utils
    from timber.timber import Timber

    from trivia.addQueuedGamesResult import AddQueuedGamesResult
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.triviaSettingsRepository import TriviaSettingsRepository


class QueuedTriviaGameStore():

    def __init__(
        self,
        timber: Timber,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaSettingsRepository is None:
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__timber: Timber = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository
        self.__queuedSuperGames: Dict[str, SimpleQueue[StartNewSuperTriviaGameAction]] = defaultdict(lambda: SimpleQueue())

    async def addSuperGames(
        self,
        isSuperTriviaGameCurrentlyInProgress: bool,
        action: StartNewSuperTriviaGameAction
    ) -> AddQueuedGamesResult:
        if not utils.isValidBool(isSuperTriviaGameCurrentlyInProgress):
            raise ValueError(f'isSuperTriviaGameCurrentlyInProgress argument is malformed: \"{isSuperTriviaGameCurrentlyInProgress}\"')
        elif action is None:
            raise ValueError(f'action argument is malformed: \"{action}\"')

        twitchChannel = action.getTwitchChannel().lower()
        queuedSuperGames = self.__queuedSuperGames[twitchChannel]
        oldQueueSize = queuedSuperGames.qsize()

        if not action.hasNumberOfGames() or action.isNumberOfGamesConsumed():
            return AddQueuedGamesResult(
                amountAdded = 0,
                newQueueSize = oldQueueSize,
                oldQueueSize = oldQueueSize
            )

        action.consumeNumberOfGames()
        maxSuperGameQueueSize = await self.__triviaSettingsRepository.getMaxSuperGameQueueSize()

        if maxSuperGameQueueSize < 1:
            return AddQueuedGamesResult(
                amountAdded = 0,
                newQueueSize = oldQueueSize,
                oldQueueSize = oldQueueSize
            )

        numberOfGames = action.getNumberOfGames()

        if not isSuperTriviaGameCurrentlyInProgress:
            numberOfGames = numberOfGames - 1

            if numberOfGames < 1:
                return AddQueuedGamesResult(
                    amountAdded = 0,
                    newQueueSize = oldQueueSize,
                    oldQueueSize = oldQueueSize
                )

        amountAdded: int = 0

        for _ in range(numberOfGames):
            if queuedSuperGames.qsize() < maxSuperGameQueueSize:
                queuedSuperGames.put(action)
                amountAdded = amountAdded + 1
            else:
                break

        return AddQueuedGamesResult(
            amountAdded = amountAdded,
            newQueueSize = queuedSuperGames.qsize(),
            oldQueueSize = oldQueueSize
        )

    async def popQueuedSuperGames(self, activeChannels: List[str]) -> List[StartNewSuperTriviaGameAction]:
        workingActiveChannels: Set[str] = set()
        for activeChannel in activeChannels:
            workingActiveChannels.add(activeChannel.lower())

        superGames: List[StartNewSuperTriviaGameAction] = list()

        for twitchChannel, queuedSuperGames in self.__queuedSuperGames.items():
            if twitchChannel.lower() in workingActiveChannels:
                continue
            elif queuedSuperGames.empty():
                continue

            try:
                superGames.append(queuedSuperGames.get_nowait())
            except queue.Empty as e:
                self.__timber.log('QueuedTriviaGameStore', f'Unable to get queued super game for \"{twitchChannel}\" (queue size: {queuedSuperGames.qsize()}): {repr(e)}')

        return superGames
