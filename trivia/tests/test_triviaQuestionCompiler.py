from typing import List

import pytest

try:
    from ...trivia.triviaQuestionCompiler import TriviaQuestionCompiler
except:
    from trivia.triviaQuestionCompiler import TriviaQuestionCompiler


class TestTriviaQuestionCompiler():

    triviaQuestionCompiler: TriviaQuestionCompiler = TriviaQuestionCompiler()

    @pytest.mark.asyncio
    async def test_compileCategory_withNone(self):
        category: str = None
        exception: Exception = None

        try:
            category = await self.triviaQuestionCompiler.compileCategory(None)
        except Exception as e:
            exception = e

        assert category is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileCategory_withEmptyString(self):
        category: str = None
        exception: Exception = None

        try:
            category = await self.triviaQuestionCompiler.compileCategory('')
        except Exception as e:
            exception = e

        assert category is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileCategory_withWhitespaceString(self):
        category: str = None
        exception: Exception = None

        try:
            category = await self.triviaQuestionCompiler.compileCategory(' ')
        except Exception as e:
            exception = e

        assert category is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileQuestion_withEllipsis(self):
        question: str = await self.triviaQuestionCompiler.compileQuestion('...And Justice for All')
        assert question is not None
        assert question == '…And Justice for All'

    @pytest.mark.asyncio
    async def test_compileQuestion_withEmptyString(self):
        question: str = None
        exception: Exception = None

        try:
            question = await self.triviaQuestionCompiler.compileQuestion('')
        except Exception as e:
            exception = e

        assert question is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileQuestion_withBbCodeTags(self):
        question: str = await self.triviaQuestionCompiler.compileQuestion('[b]Scenes from a Memory[/b]')
        assert question is not None
        assert question == 'Scenes from a Memory'

    @pytest.mark.asyncio
    async def test_compileQuestion_withHtmlTags(self):
        question: str = await self.triviaQuestionCompiler.compileQuestion('<i>The Great Misdirect</i>')
        assert question is not None
        assert question == 'The Great Misdirect'

    @pytest.mark.asyncio
    async def test_compileQuestion_withManyUnderscores(self):
        question: str = await self.triviaQuestionCompiler.compileQuestion('The _________ river is very long.')
        assert question is not None
        assert question == 'The ___ river is very long.'

    @pytest.mark.asyncio
    async def test_compileQuestion_withNone(self):
        question: str = None
        exception: Exception = None

        try:
            question = await self.triviaQuestionCompiler.compileQuestion(None)
        except Exception as e:
            exception = e

        assert question is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileQuestion_withWhitespaceString(self):
        question: str = None
        exception: Exception = None

        try:
            question = await self.triviaQuestionCompiler.compileQuestion(' ')
        except Exception as e:
            exception = e

        assert question is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileResponse_withEmptyString(self):
        response: str = None
        exception: Exception = None

        try:
            response = await self.triviaQuestionCompiler.compileResponse('')
        except Exception as e:
            exception = e

        assert response is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileResponse_withNone(self):
        response: str = None
        exception: Exception = None

        try:
            response = await self.triviaQuestionCompiler.compileResponse(None)
        except Exception as e:
            exception = e

        assert response is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileResponse_withWhitespaceString(self):
        response: str = None
        exception: Exception = None

        try:
            response = await self.triviaQuestionCompiler.compileResponse(' ')
        except Exception as e:
            exception = e

        assert response is None
        assert isinstance(exception, ValueError)

    @pytest.mark.asyncio
    async def test_compileResponses_withEmptyList(self):
        responses: List[str] = await self.triviaQuestionCompiler.compileResponses(list())
        assert responses is not None
        assert len(responses) == 0

    @pytest.mark.asyncio
    async def test_compileResponses_withMixedList(self):
        responses: List[str] = await self.triviaQuestionCompiler.compileResponses(
            [ '', ' ', 'One', '', 'Two', '\n', 'Three' ]
        )
        assert responses is not None
        assert len(responses) == 3
        assert 'One' in responses
        assert 'Two' in responses
        assert 'Three' in responses

    @pytest.mark.asyncio
    async def test_compileResponses_withNone(self):
        responses: List[str] = await self.triviaQuestionCompiler.compileResponses(None)
        assert responses is not None
        assert len(responses) == 0

    def test_sanity(self):
        assert self.triviaQuestionCompiler is not None
        assert isinstance(self.triviaQuestionCompiler, TriviaQuestionCompiler)
