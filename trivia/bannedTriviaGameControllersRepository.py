from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.administratorProviderInterface import \
        AdministratorProviderInterface
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.trivia.addBannedTriviaGameControllerResult import \
        AddBannedTriviaGameControllerResult
    from CynanBotCommon.trivia.bannedTriviaGameController import \
        BannedTriviaGameController
    from CynanBotCommon.trivia.removeBannedTriviaGameControllerResult import \
        RemoveBannedTriviaGameControllerResult
    from CynanBotCommon.twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from CynanBotCommon.users.userIdsRepositoryInterface import \
        UserIdsRepositoryInterface
except:
    import utils
    from administratorProviderInterface import AdministratorProviderInterface
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface
    from trivia.addBannedTriviaGameControllerResult import \
        AddBannedTriviaGameControllerResult
    from trivia.bannedTriviaGameController import BannedTriviaGameController
    from trivia.removeBannedTriviaGameControllerResult import \
        RemoveBannedTriviaGameControllerResult

    from twitch.twitchTokensRepositoryInterface import \
        TwitchTokensRepositoryInterface
    from users.userIdsRepositoryInterface import UserIdsRepositoryInterface


class BannedTriviaGameControllersRepository():

    def __init__(
        self,
        administratorProvider: AdministratorProviderInterface,
        backingDatabase: BackingDatabase,
        timber: TimberInterface,
        twitchTokensRepository: TwitchTokensRepositoryInterface,
        userIdsRepository: UserIdsRepositoryInterface
    ):
        if not isinstance(administratorProvider, AdministratorProviderInterface):
            raise ValueError(f'administratorProviderInterface argument is malformed: \"{administratorProvider}\"')
        elif not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchTokensRepository, TwitchTokensRepositoryInterface):
            raise ValueError(f'twitchTokensRepositoryInterface argument is malformed: \"{twitchTokensRepository}\"')
        elif not isinstance(userIdsRepository, UserIdsRepositoryInterface):
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')

        self.__administratorProvider: AdministratorProviderInterface = administratorProvider
        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber
        self.__twitchTokensRepositoryInterface: TwitchTokensRepositoryInterface = twitchTokensRepository
        self.__userIdsRepository: UserIdsRepositoryInterface = userIdsRepository

        self.__isDatabaseReady: bool = False

    async def addBannedController(self, userName: str) -> AddBannedTriviaGameControllerResult:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        administrator = await self.__administratorProvider.getAdministratorUserName()
        twitchAccessToken = await self.__twitchTokensRepositoryInterface.getAccessToken(administrator)

        userId = await self.__userIdsRepository.fetchUserId(
            userName = userName,
            twitchAccessToken = twitchAccessToken
        )

        if not utils.isValidStr(userId):
            self.__timber.log('BannedTriviaGameControllersRepository', f'Retrieved no userId from UserIdsRepository when trying to add \"{userName}\" as a banned trivia game controller: \"{userId}\"')
            return AddBannedTriviaGameControllerResult.ERROR

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT COUNT(1) FROM bannedtriviagamecontrollers
                WHERE userid = $1
                LIMIT 1
            ''',
            userId
        )

        count: Optional[int] = None
        if utils.hasItems(record):
            count = record[0]

        if utils.isValidInt(count) and count >= 1:
            await connection.close()
            self.__timber.log('BannedTriviaGameControllersRepository', f'Tried to add userName=\"{userName}\" userId=\"{userId}\" as a banned trivia game controller, but this user has already been added as one')
            return AddBannedTriviaGameControllerResult.ALREADY_EXISTS

        await connection.execute(
            '''
                INSERT INTO bannedtriviagamecontrollers (userid)
                VALUES ($1)
                ON CONFLICT (userid) DO NOTHING
            ''',
            userId
        )

        await connection.close()
        self.__timber.log('BannedTriviaGameControllersRepository', f'Added userName=\"{userName}\" userId=\"{userId}\" as a banned trivia game controller')

        return AddBannedTriviaGameControllerResult.ADDED

    async def getBannedControllers(self) -> List[BannedTriviaGameController]:
        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT bannedtriviagamecontrollers.userid, userids.username FROM bannedtriviagamecontrollers
                INNER JOIN userids ON bannedtriviagamecontrollers.userid = userids.userid
                ORDER BY userids.username ASC
            '''
        )

        controllers: List[BannedTriviaGameController] = list()

        if not utils.hasItems(records):
            await connection.close()
            return controllers

        for record in records:
            controllers.append(BannedTriviaGameController(
                userId = record[0],
                userName = record[1]
            ))

        await connection.close()
        controllers.sort(key = lambda controller: controller.getUserName().lower())

        return controllers

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS bannedtriviagamecontrollers (
                        userid public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS bannedtriviagamecontrollers (
                        userid TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def removeBannedController(self, userName: str) -> RemoveBannedTriviaGameControllerResult:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        userId = await self.__userIdsRepository.fetchUserId(userName = userName)

        if not utils.isValidStr(userId):
            self.__timber.log('BannedTriviaGameControllersRepository', f'Retrieved no userId from UserIdsRepository when trying to remove \"{userName}\" as a banned trivia game controller')
            return RemoveBannedTriviaGameControllerResult.ERROR

        connection = await self.__backingDatabase.getConnection()
        await connection.execute(
            '''
                DELETE FROM bannedtriviagamecontrollers
                WHERE userid = $1
            ''',
            userId
        )

        await connection.close()
        self.__timber.log('BannedTriviaGameControllersRepository', f'Removed userName=\"{userName}\" userId=\"{userId}\" as a banned trivia game controller')

        return RemoveBannedTriviaGameControllerResult.REMOVED
