from abc import ABC, abstractmethod
from typing import Optional

try:
    from CynanBotCommon.trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from CynanBotCommon.trivia.startNewTriviaGameAction import \
        StartNewTriviaGameAction
except:
    from trivia.startNewSuperTriviaGameAction import \
        StartNewSuperTriviaGameAction
    from trivia.startNewTriviaGameAction import StartNewTriviaGameAction    


class TriviaGameBuilderInterface(ABC):

    @abstractmethod
    async def createNewTriviaGame(
        self,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> Optional[StartNewTriviaGameAction]:
        pass

    @abstractmethod
    async def createNewSuperTriviaGame(
        self,
        twitchChannel: str,
        numberOfGames: int = 1
    ) -> Optional[StartNewSuperTriviaGameAction]:
        pass
