try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.funtoon.funtoonRepositoryInterface import \
        FuntoonRepositoryInterface
    from CynanBotCommon.trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from CynanBotCommon.trivia.banTriviaQuestionResult import \
        BanTriviaQuestionResult
    from CynanBotCommon.trivia.triviaBanHelperInterface import \
        TriviaBanHelperInterface
    from CynanBotCommon.trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from funtoon.funtoonRepositoryInterface import FuntoonRepositoryInterface
    from trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from trivia.banTriviaQuestionResult import BanTriviaQuestionResult
    from trivia.triviaBanHelperInterface import TriviaBanHelperInterface
    from trivia.triviaSettingsRepositoryInterface import \
        TriviaSettingsRepositoryInterface
    from trivia.triviaSource import TriviaSource


class TriviaBanHelper(TriviaBanHelperInterface):

    def __init__(
        self,
        bannedTriviaIdsRepository: BannedTriviaIdsRepositoryInterface,
        funtoonRepository: FuntoonRepositoryInterface,
        triviaSettingsRepository: TriviaSettingsRepositoryInterface
    ):
        if not isinstance(bannedTriviaIdsRepository, BannedTriviaIdsRepositoryInterface):
            raise ValueError(f'bannedTriviaIdsRepository argument is malformed: \"{bannedTriviaIdsRepository}\"')
        elif not isinstance(funtoonRepository, FuntoonRepositoryInterface):
            raise ValueError(f'funtoonRepository argument is malformed: \"{funtoonRepository}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepositoryInterface):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__bannedTriviaIdsRepository: BannedTriviaIdsRepositoryInterface = bannedTriviaIdsRepository
        self.__funtoonRepository: FuntoonRepositoryInterface = funtoonRepository
        self.__triviaSettingsRepository: TriviaSettingsRepositoryInterface = triviaSettingsRepository

    async def ban(
        self,
        triviaId: str,
        userId: str,
        triviaSource: TriviaSource
    ) -> BanTriviaQuestionResult:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if triviaSource is TriviaSource.FUNTOON:
            await self.__funtoonRepository.banTriviaQuestion(triviaId)
            return BanTriviaQuestionResult.BANNED
        else:
            return await self.__bannedTriviaIdsRepository.ban(
                triviaId = triviaId,
                userId = userId,
                triviaSource = triviaSource
            )

    async def isBanned(self, triviaId: str, triviaSource: TriviaSource) -> bool:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if not await self.__triviaSettingsRepository.isBanListEnabled():
            return False

        return await self.__bannedTriviaIdsRepository.isBanned(
            triviaId = triviaId,
            triviaSource = triviaSource
        )

    async def unban(
        self,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> BanTriviaQuestionResult:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        return await self.__bannedTriviaIdsRepository.unban(
            triviaId = triviaId,
            triviaSource = triviaSource
        )
