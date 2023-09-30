from abc import ABC, abstractmethod
from typing import Set

try:
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.triviaFetchOptions import TriviaFetchOptions
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.triviaFetchOptions import TriviaFetchOptions
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class TriviaQuestionRepositoryInterface(ABC):

    @abstractmethod
    async def fetchTriviaQuestion(self, fetchOptions: TriviaFetchOptions) -> AbsTriviaQuestion:
        pass

    @abstractmethod
    def getSupportedTriviaTypes(self) -> Set[TriviaType]:
        pass

    @abstractmethod
    def getTriviaSource(self) -> TriviaSource:
        pass

    @abstractmethod
    async def hasQuestionSetAvailable(self) -> bool:
        pass
