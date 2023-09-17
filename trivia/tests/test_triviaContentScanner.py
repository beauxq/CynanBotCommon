from typing import List

import pytest

try:
    from ...storage.jsonStaticReader import JsonStaticReader
    from ...storage.linesReaderInterface import LinesReaderInterface
    from ...storage.linesStaticReader import LinesStaticReader
    from ...timber.timberInterface import TimberInterface
    from ...timber.timberStub import TimberStub
    from ...trivia.absTriviaQuestion import AbsTriviaQuestion
    from ...trivia.bannedWords.bannedWordsRepository import \
        BannedWordsRepository
    from ...trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from ...trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from ...trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from ...trivia.triviaContentCode import TriviaContentCode
    from ...trivia.triviaContentScanner import TriviaContentScanner
    from ...trivia.triviaContentScannerInterface import \
        TriviaContentScannerInterface
    from ...trivia.triviaDifficulty import TriviaDifficulty
    from ...trivia.triviaSettingsRepository import TriviaSettingsRepository
    from ...trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from ...trivia.triviaSource import TriviaSource
    from ...trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion
except:
    from storage.jsonStaticReader import JsonStaticReader
    from storage.linesReaderInterface import LinesReaderInterface
    from storage.linesStaticReader import LinesStaticReader
    from timber.timberInterface import TimberInterface
    from timber.timberStub import TimberStub
    from trivia.absTriviaQuestion import AbsTriviaQuestion
    from trivia.bannedWords.bannedWordsRepository import BannedWordsRepository
    from trivia.bannedWords.bannedWordsRepositoryInterface import \
        BannedWordsRepositoryInterface
    from trivia.multipleChoiceTriviaQuestion import \
        MultipleChoiceTriviaQuestion
    from trivia.questionAnswerTriviaQuestion import \
        QuestionAnswerTriviaQuestion
    from trivia.triviaContentCode import TriviaContentCode
    from trivia.triviaContentScanner import TriviaContentScanner
    from trivia.triviaContentScannerInterface import \
        TriviaContentScannerInterface
    from trivia.triviaDifficulty import TriviaDifficulty
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from trivia.triviaSource import TriviaSource
    from trivia.trueFalseTriviaQuestion import TrueFalseTriviaQuestion


class TestTriviaContentScanner():

    triviaSettingsRepository: TriviaSettingsRepositoryInterface = TriviaSettingsRepository(
        settingsJsonReader = JsonStaticReader(dict())
    )

    bannedWordsLinesReader: LinesReaderInterface = LinesStaticReader(
        lines = [ 'bitch', '"trump"' ]
    )

    timber: TimberInterface = TimberStub()

    bannedWordsRepositoryInterface: BannedWordsRepositoryInterface = BannedWordsRepository(
        bannedWordsLinesReader = bannedWordsLinesReader,
        timber = timber
    )

    triviaContentScanner: TriviaContentScannerInterface = TriviaContentScanner(
        bannedWordsRepository = bannedWordsRepositoryInterface,
        timber = timber,
        triviaSettingsRepository = triviaSettingsRepository
    )

    @pytest.mark.asyncio
    async def test_verify_withGnarlyTriviaQuestion1(self):
        correctAnswers: List[bool] = list()
        correctAnswers.append(False)

        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = correctAnswers,
            category = None,
            categoryId = None,
            question = 'QAnon is Trump fighting the deep state and it\'s real.',
            triviaId = 'asdfasdfasdf',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.OPEN_TRIVIA_QA
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.CONTAINS_BANNED_WORD

    @pytest.mark.asyncio
    async def test_verify_withGnarlyTriviaQuestion2(self):
        correctAnswers: List[bool] = list()
        correctAnswers.append('two')

        multipleChoiceResponses: List[str] = list()
        multipleChoiceResponses.append('one')
        multipleChoiceResponses.append('two')
        multipleChoiceResponses.append('three')

        question: AbsTriviaQuestion = MultipleChoiceTriviaQuestion(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = multipleChoiceResponses,
            category = None,
            categoryId = None,
            question = 'bitching', # the banned word is actually "bitch", but
                                   # that word is hidden within "bitching", so
                                   # this question should end up banned
            triviaId = 'asdfasdfasdf',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.J_SERVICE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.CONTAINS_BANNED_WORD

    @pytest.mark.asyncio
    async def test_verify_withTriviaQuestionThatAlmostContainsBannedWord(self):
        # the banned word is "trump", but this answer contains "trumpet", which is not banned
        correctAnswers: List[str] = list()
        correctAnswers.append('a trumpet')

        cleanedCorrectAnswers: List[str] = list()
        cleanedCorrectAnswers.append('trumpet')

        question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
            correctAnswers = correctAnswers,
            cleanedCorrectAnswers = cleanedCorrectAnswers,
            category = None,
            categoryId = None,
            question = 'This instrument is made from brass.', 
            triviaId = 'asdfasdfasdf',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.FUNTOON
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK

    @pytest.mark.asyncio
    async def test_verify_withNone(self):
        result = await self.triviaContentScanner.verify(None)
        assert result is TriviaContentCode.IS_NONE

    @pytest.mark.asyncio
    async def test_verify_withSimpleTriviaQuestion1(self):
        correctAnswers: List[bool] = list()
        correctAnswers.append(True)

        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = correctAnswers,
            category = None,
            categoryId = None,
            question = 'What is?',
            triviaId = 'abc123',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.TRIVIA_DATABASE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK

    @pytest.mark.asyncio
    async def test_verify_withSimpleTriviaQuestion2(self):
        correctAnswers: List[bool] = list()
        correctAnswers.append(False)

        question: AbsTriviaQuestion = TrueFalseTriviaQuestion(
            correctAnswers = correctAnswers,
            category = None,
            categoryId = None,
            question = 'Blah blah question here?',
            triviaId = 'abc456',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.J_SERVICE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK

    @pytest.mark.asyncio
    async def test_verify_withSimpleTriviaQuestion3(self):
        correctAnswers: List[str] = list()
        correctAnswers.append('Nintendo 64')

        multipleChoiceResponses: List[str] = list()
        multipleChoiceResponses.append('Nintendo Entertainment System')
        multipleChoiceResponses.append('Nintendo 64')
        multipleChoiceResponses.append('Sony PlayStation')

        question: AbsTriviaQuestion = MultipleChoiceTriviaQuestion(
            correctAnswers = correctAnswers,
            multipleChoiceResponses = multipleChoiceResponses,
            category = None,
            categoryId = None,
            question = 'What is \"N64\" an abbreviation for?',
            triviaId = 'qwerty',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK

    @pytest.mark.asyncio
    async def test_verify_withSimpleTriviaQuestion4(self):
        correctAnswers: List[str] = list()
        correctAnswers.append('(King) James')

        cleanedCorrectAnswers: List[str] = list()
        cleanedCorrectAnswers.append('(King) James')

        question: AbsTriviaQuestion = QuestionAnswerTriviaQuestion(
            correctAnswers = correctAnswers,
            cleanedCorrectAnswers = cleanedCorrectAnswers,
            category = None,
            categoryId = None,
            question = 'Who was a king from way back?',
            triviaId = 'azerty',
            triviaDifficulty = TriviaDifficulty.UNKNOWN,
            triviaSource = TriviaSource.OPEN_TRIVIA_DATABASE
        )

        result = await self.triviaContentScanner.verify(question)
        assert result is TriviaContentCode.OK
