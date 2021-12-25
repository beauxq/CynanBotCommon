from abc import ABC, abstractmethod
from typing import List

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils

    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class AbsTriviaQuestion(ABC):

    def __init__(
        self,
        category: str,
        _id: str,
        question: str,
        triviaDifficulty: TriviaDifficulty,
        triviaSource: TriviaSource,
        triviaType: TriviaType
    ):
        if not utils.isValidStr(question):
            raise ValueError(f'question argument is malformed: \"{question}\"')
        elif triviaDifficulty is None:
            raise ValueError(f'triviaDifficulty argument is malformed: \"{triviaDifficulty}\"')
        elif triviaSource is None:
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')
        elif triviaType is None:
            raise ValueError(f'triviaType argument is malformed: \"{triviaType}\"')

        self.__category: str = category
        self.__id: str = _id
        self.__question: str = question
        self.__triviaDifficulty: TriviaDifficulty = triviaDifficulty
        self.__triviaSource: TriviaSource = triviaSource
        self.__triviaType: TriviaType = triviaType

    def getAnswerReveal(self, delimiter: str = ', ') -> str:
        if delimiter is None:
            raise ValueError(f'delimiter argument is malformed: \"{delimiter}\"')

        correctAnswers = self.getCorrectAnswers()
        return delimiter.join(correctAnswers)

    def getCategory(self) -> str:
        return self.__category

    @abstractmethod
    def getCorrectAnswers(self) -> List[str]:
        pass

    def getId(self) -> str:
        return self.__id

    @abstractmethod
    def getPrompt(self, delimiter: str = ', ') -> str:
        pass

    def getQuestion(self) -> str:
        return self.__question

    @abstractmethod
    def getResponses(self) -> List[str]:
        pass

    def getTriviaDifficulty(self) -> TriviaDifficulty:
        return self.__triviaDifficulty

    def getTriviaSource(self) -> TriviaSource:
        return self.__triviaSource

    def getTriviaType(self) -> TriviaType:
        return self.__triviaType

    def hasCategory(self) -> bool:
        return utils.isValidStr(self.__category)

    def hasId(self) -> bool:
        return utils.isValidStr(self.__id)