from typing import Dict, List, Optional

import aiosqlite

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.absTriviaQuestion import AbsTriviaQuestion
    from CynanBotCommon.trivia.absTriviaQuestionRepository import \
        AbsTriviaQuestionRepository
    from CynanBotCommon.trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from CynanBotCommon.trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from CynanBotCommon.trivia.triviaDifficulty import TriviaDifficulty
    from CynanBotCommon.trivia.triviaQuestionCompiler import \
        TriviaQuestionCompiler
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
    from CynanBotCommon.trivia.triviaType import TriviaType
except:
    import utils
    from timber.timber import Timber

    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.absTriviaQuestionRepository import AbsTriviaQuestionRepository
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaAnswerCompiler import TriviaAnswerCompiler
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource
    from trivia.triviaType import TriviaType


class LotrTriviaQuestionRepository(AbsTriviaQuestionRepository):

    def __init__(
        self,
        timber: Timber,
        triviaAnswerCompiler: TriviaAnswerCompiler,
        triviaQuestionCompiler: TriviaQuestionCompiler,
        triviaSettingsRepository: TriviaSettingsRepository,
        triviaDatabaseFile: str = 'CynanBotCommon/trivia/lotrTriviaQuestionsDatabase.sqlite'
    ):
        super().__init__(triviaSettingsRepository)

        if timber is None:
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif triviaAnswerCompiler is None:
            raise ValueError(f'triviaAnswerCompiler argument is malformed: \"{triviaAnswerCompiler}\"')
        elif triviaQuestionCompiler is None:
            raise ValueError(f'triviaQuestionCompiler argument is malformed: \"{triviaQuestionCompiler}\"')
        elif not utils.isValidStr(triviaDatabaseFile):
            raise ValueError(f'triviaDatabaseFile argument is malformed: \"{triviaDatabaseFile}\"')

        self.__timber: Timber = timber
        self.__triviaAnswerCompiler: TriviaAnswerCompiler = triviaAnswerCompiler
        self.__triviaQuestionCompiler: TriviaQuestionCompiler = triviaQuestionCompiler
        self.__triviaDatabaseFile: str = triviaDatabaseFile

    async def fetchTriviaQuestion(self, twitchChannel: Optional[str]) -> AbsTriviaQuestion:
        self.__timber.log('LotrTriviaQuestionRepository', 'Fetching trivia question...')

        triviaDict = await self.__fetchTriviaQuestionDict()

        if await self._triviaSettingsRepository.isDebugLoggingEnabled():
            self.__timber.log('LotrTriviaQuestionRepository', f'{triviaDict}')

        triviaId = utils.getStrFromDict(triviaDict, 'triviaId')
        question = await self.__triviaQuestionCompiler.compileQuestion(utils.getStrFromDict(triviaDict, 'question'))

        correctAnswers: List[str] = triviaDict['correctAnswers']
        cleanedCorrectAnswers = await self.__triviaAnswerCompiler.compileTextAnswersList(correctAnswers)

        return QuestionAnswerTriviaQuestion(
            correctAnswers = correctAnswers,
            cleanedCorrectAnswers = cleanedCorrectAnswers,
            category = 'Lord of the Rings',
            question = question,
            triviaId = triviaId,
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.LORD_OF_THE_RINGS
        )

    async def __fetchTriviaQuestionDict(self) -> Dict[str, object]:
        connection = await aiosqlite.connect(self.__triviaDatabaseFile)
        cursor = await connection.execute(
            '''
                SELECT answerA, answerB, answerC, answerD, question, triviaId FROM lotrQuestions
                ORDER BY RANDOM()
                LIMIT 1
            '''
        )

        row = await cursor.fetchone()
        if not utils.hasItems(row) or len(row) != 6:
            raise RuntimeError(f'Received malformed data from LOTR database: {row}')

        correctAnswers: List[str] = list()
        self.__selectiveAppend(correctAnswers, row[0])
        self.__selectiveAppend(correctAnswers, row[1])
        self.__selectiveAppend(correctAnswers, row[2])
        self.__selectiveAppend(correctAnswers, row[3])

        if not utils.hasItems(correctAnswers):
            raise RuntimeError(f'Received malformed correct answer data from LOTR database: {row}')

        triviaQuestionDict: Dict[str, object] = {
            'correctAnswers': correctAnswers,
            'question': row[4],
            'triviaId': row[5]
        }

        await cursor.close()
        await connection.close()
        return triviaQuestionDict

    def getSupportedTriviaTypes(self) -> List[TriviaType]:
        return [ TriviaType.QUESTION_ANSWER ]

    def getTriviaSource(self) -> TriviaSource:
        return TriviaSource.LORD_OF_THE_RINGS

    def __selectiveAppend(self, correctAnswers: List[str], correctAnswer: str):
        if correctAnswers is None:
            raise ValueError(f'correctAnswers argument is malformed: \"{correctAnswers}\"')

        if utils.isValidStr(correctAnswer):
            correctAnswers.append(correctAnswer)
