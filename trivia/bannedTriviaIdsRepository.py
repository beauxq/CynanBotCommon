from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from CynanBotCommon.trivia.bannedTriviaQuestion import BannedTriviaQuestion
    from CynanBotCommon.trivia.banTriviaQuestionResult import \
        BanTriviaQuestionResult
    from CynanBotCommon.trivia.triviaSettingsRepository import \
        TriviaSettingsRepository
    from CynanBotCommon.trivia.triviaSource import TriviaSource
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface
    from trivia.bannedTriviaIdsRepositoryInterface import \
        BannedTriviaIdsRepositoryInterface
    from trivia.bannedTriviaQuestion import BannedTriviaQuestion
    from trivia.banTriviaQuestionResult import BanTriviaQuestionResult
    from trivia.triviaSettingsRepository import TriviaSettingsRepository
    from trivia.triviaSource import TriviaSource


class BannedTriviaIdsRepository(BannedTriviaIdsRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface,
        triviaSettingsRepository: TriviaSettingsRepository
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(triviaSettingsRepository, TriviaSettingsRepository):
            raise ValueError(f'triviaSettingsRepository argument is malformed: \"{triviaSettingsRepository}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber
        self.__triviaSettingsRepository: TriviaSettingsRepository = triviaSettingsRepository

        self.__isDatabaseReady: bool = False

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

        info = await self.getInfo(triviaId = triviaId, triviaSource = triviaSource)

        if info is not None:
            self.__timber.log('BannedTriviaIdsRepository', f'Attempted to ban trivia question but it\'s already been banned: {info}')
            return BanTriviaQuestionResult.ALREADY_BANNED

        self.__timber.log('BannedTriviaIdsRepository', f'Banning trivia question (triviaId=\"{triviaId}\", userId=\"{userId}\", triviaSource=\"{triviaSource}\")...')

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO bannedtriviaids (triviaid, triviasource, userid)
                VALUES ($1, $2, $3)
            ''',
            triviaId, triviaSource.toStr(), userId
        )

        await connection.close()
        self.__timber.log('BannedTriviaIdsRepository', f'Banned trivia question (triviaId=\"{triviaId}\", userId=\"{userId}\", triviaSource=\"{triviaSource}\")')

        return BanTriviaQuestionResult.BANNED

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def getInfo(
        self,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> Optional[BannedTriviaQuestion]:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT bannedtriviaids.triviaid, bannedtriviaids.triviasource, bannedtriviaids.userid, userids.username FROM bannedtriviaids
                INNER JOIN userids ON bannedtriviaids.userid = userids.userid
                WHERE bannedtriviaids.triviaid = $1 AND bannedtriviaids.triviasource = $2
                LIMIT 1
            ''',
            triviaId, triviaSource.toStr()
        )

        await connection.close()

        if not utils.hasItems(record):
            return None

        return BannedTriviaQuestion(
            triviaId = record[0],
            userId = record[2],
            userName = record[3],
            triviaSource = TriviaSource.fromStr(record[1])
        )

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS bannedtriviaids (
                        triviaid public.citext NOT NULL,
                        triviasource public.citext NOT NULL,
                        userid public.citext NOT NULL,
                        PRIMARY KEY (triviaid, triviasource)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS bannedtriviaids (
                        triviaid TEXT NOT NULL COLLATE NOCASE,
                        triviasource TEXT NOT NULL COLLATE NOCASE,
                        userid TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (triviaid, triviasource)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def isBanned(self, triviaId: str, triviaSource: TriviaSource) -> bool:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        if not await self.__triviaSettingsRepository.isBanListEnabled():
            return False

        bannedTriviaQuestion = await self.getInfo(
            triviaId = triviaId,
            triviaSource = triviaSource
        )

        if bannedTriviaQuestion is None:
            return False

        self.__timber.log('BannedTriviaIdsRepository', f'Encountered banned trivia question ({bannedTriviaQuestion})')
        return True

    async def unban(
        self,
        triviaId: str,
        triviaSource: TriviaSource
    ) -> BanTriviaQuestionResult:
        if not utils.isValidStr(triviaId):
            raise ValueError(f'triviaId argument is malformed: \"{triviaId}\"')
        elif not isinstance(triviaSource, TriviaSource):
            raise ValueError(f'triviaSource argument is malformed: \"{triviaSource}\"')

        info = await self.getInfo(triviaId = triviaId, triviaSource = triviaSource)

        if info is None:
            self.__timber.log('BannedTriviaIdsRepository', f'Attempted to unban trivia question but it wasn\'t banned (triviaId=\"{triviaId}\", triviaSource=\"{triviaSource}\")')
            return BanTriviaQuestionResult.NOT_BANNED

        self.__timber.log('BannedTriviaIdsRepository', f'Unbanning trivia question (triviaId=\"{triviaId}\", triviaSource=\"{triviaSource}\")...')

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                DELETE FROM bannedtriviaids
                WHERE triviaid = $1 AND triviasource = $2
            ''',
            triviaId, triviaSource.toStr()
        )

        await connection.close()
        self.__timber.log('BannedTriviaIdsRepository', f'Unbanned trivia question (triviaId=\"{triviaId}\", triviaSource=\"{triviaSource}\")')

        return BanTriviaQuestionResult.UNBANNED
