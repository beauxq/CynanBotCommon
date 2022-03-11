import json
import os
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils

    from trivia.triviaSource import TriviaSource


class GeneralTriviaSettingsRepository():

    def __init__(
        self,
        generalSettingsFile: str = ''
    ):
        if not utils.isValidStr(generalSettingsFile):
            raise ValueError(f'generalSettingsFile argument is malformed: \"{generalSettingsFile}\"')

        self.__generalSettingsFile: str = generalSettingsFile

    def getAvailableTriviaSourcesAndWeights(
        self,
        isJokeTriviaRepositoryEnabled: bool = False
    ) -> Dict[TriviaSource, int]:
        if not utils.isValidBool(isJokeTriviaRepositoryEnabled):
            raise ValueError(f'isJokeTriviaRepositoryEnabled argument is malformed: \"{isJokeTriviaRepositoryEnabled}\"')

        jsonContents = self.__readJson()

        triviaSourcesJson: Dict[str, object] = jsonContents['trivia_sources']
        if not utils.hasItems(triviaSourcesJson):
            raise RuntimeError(f'\"trivia_sources\" field in \"{self.__generalSettingsFile}\" is malformed: \"{triviaSourcesJson}\"')

        triviaSources: Dict[TriviaSource, int] = dict()

        for key in triviaSourcesJson:
            triviaSource = TriviaSource.fromStr(key)

            if triviaSource is TriviaSource.JOKE_TRIVIA_REPOSITORY and not isJokeTriviaRepositoryEnabled:
                continue
            elif triviaSource is TriviaSource.QUIZ_API and not self.hasQuizApiKey():
                continue

            triviaSourceJson: Dict[str, object] = triviaSourcesJson[key]

            isEnabled = utils.getBoolFromDict(triviaSourceJson, 'is_enabled', False)
            if not isEnabled:
                continue

            weight = utils.getIntFromDict(triviaSourceJson, 'weight', 1)
            if weight < 1:
                raise ValueError(f'triviaSource \"{triviaSource}\" in \"{self.__generalSettingsFile}\" has an invalid weight: \"{weight}\"')

            triviaSources[triviaSource] = weight

        if not utils.hasItems(triviaSources):
            raise RuntimeError(f'triviaSources is empty: \"{triviaSources}\"')

        return triviaSources

    def getMaxMultipleChoiceResponses(self) -> int:
        jsonContents = self.__readJson()
        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 5)
        minMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'min_multiple_choice_responses', 2)

        if maxMultipleChoiceResponses < 2:
            raise ValueError(f'maxMultipleChoiceResponses is too small: {maxMultipleChoiceResponses}')
        elif maxMultipleChoiceResponses < minMultipleChoiceResponses:
            raise ValueError(f'maxMultipleChoiceResponses ({maxMultipleChoiceResponses}) is less than minMultipleChoiceResponses ({minMultipleChoiceResponses})')

        return maxMultipleChoiceResponses

    def getMaxRetryCount(self) -> int:
        jsonContents = self.__readJson()
        maxRetryCount = utils.getIntFromDict(jsonContents, 'max_retry_count', 3)

        if maxRetryCount < 2:
            raise ValueError(f'maxRetryCount is too small: \"{maxRetryCount}\"')

        return maxRetryCount

    def getMinMultipleChoiceResponses(self) -> int:
        jsonContents = self.__readJson()
        maxMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'max_multiple_choice_responses', 5)
        minMultipleChoiceResponses = utils.getIntFromDict(jsonContents, 'min_multiple_choice_responses', 2)

        if minMultipleChoiceResponses < 2:
            raise ValueError(f'minMultipleChoiceResponses is too small: \"{minMultipleChoiceResponses}\"')
        elif minMultipleChoiceResponses > maxMultipleChoiceResponses:
            raise ValueError(f'minMultipleChoiceResponses ({minMultipleChoiceResponses}) is greater than maxMultipleChoiceResponses ({maxMultipleChoiceResponses})')

        return minMultipleChoiceResponses

    def getQuizApiKey(self) -> str:
        jsonContents = self.__readJson()
        return jsonContents.get('quiz_api_key')

    def hasQuizApiKey(self) -> bool:
        return utils.isValidStr(self.getQuizApiKey())

    def __readJson(self) -> Dict[str, object]:
        if not os.path.exists(self.__generalSettingsFile):
            raise FileNotFoundError(f'General trivia settings file not found: \"{self.__generalSettingsFile}\"')

        with open(self.__generalSettingsFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from general trivia settings file: \"{self.__generalSettingsFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of general trivia settings file \"{self.__generalSettingsFile}\" is empty')

        return jsonContents

    def requireQuizApiKey(self) -> str:
        quizApiKey = self.getQuizApiKey()

        if not utils.isValidStr(quizApiKey):
            raise ValueError(f'\"quiz_api_key\" in general trivia settings file \"{self.__generalSettingsFile}\" is malformed: \"{quizApiKey}\"')

        return quizApiKey
