from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timber import Timber
    from CynanBotCommon.trivia.addTriviaGameControllerResult import \
        AddTriviaGameControllerResult
    from CynanBotCommon.trivia.removeTriviaGameControllerResult import \
        RemoveTriviaGameControllerResult
    from CynanBotCommon.trivia.triviaGameController import TriviaGameController
    from CynanBotCommon.twitch.twitchTokensRepository import \
        TwitchTokensRepository
    from CynanBotCommon.users.userIdsRepository import UserIdsRepository
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timber import Timber
    from trivia.addTriviaGameControllerResult import \
        AddTriviaGameControllerResult
    from trivia.removeTriviaGameControllerResult import \
        RemoveTriviaGameControllerResult
    from trivia.triviaGameController import TriviaGameController

    from twitch.twitchTokensRepository import TwitchTokensRepository
    from users.userIdsRepository import UserIdsRepository


class TriviaGameControllersRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: Timber,
        twitchTokensRepository: TwitchTokensRepository,
        userIdsRepository: UserIdsRepository
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, Timber):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchTokensRepository, TwitchTokensRepository):
            raise ValueError(f'twitchTokensRepository argument is malformed: \"{twitchTokensRepository}\"')
        elif not isinstance(userIdsRepository, UserIdsRepository):
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: Timber = timber
        self.__twitchTokensRepository: TwitchTokensRepository = twitchTokensRepository
        self.__userIdsRepository: UserIdsRepository = userIdsRepository

        self.__isDatabaseReady: bool = False

    async def addController(
        self,
        twitchChannel: str,
        userName: str
    ) -> AddTriviaGameControllerResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        twitchAccessToken = await self.__twitchTokensRepository.getAccessToken(twitchChannel)
        userId: Optional[str] = None

        try:
            userId = await self.__userIdsRepository.fetchUserId(
                userName = userName,
                twitchAccessToken = twitchAccessToken
            )
        except (RuntimeError, ValueError) as e:
            self.__timber.log('TriviaGameControllersRepository', f'Encountered exception when trying to add \"{userName}\" as a trivia game controller for \"{twitchChannel}\": {e}', e)
            return AddTriviaGameControllerResult.ERROR

        if not utils.isValidStr(userId):
            self.__timber.log('TriviaGameControllersRepository', f'Retrieved no userId from UserIdsRepository when trying to add \"{userName}\" as a trivia game controller for \"{twitchChannel}\": \"{userId}\"')
            return AddTriviaGameControllerResult.ERROR

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT COUNT(1) FROM triviagamecontrollers
                WHERE twitchchannel = $1 AND userid = $2
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        count: Optional[int] = None
        if utils.hasItems(record):
            count = record[0]

        if utils.isValidInt(count) and count >= 1:
            await connection.close()
            self.__timber.log('TriviaGameControllersRepository', f'Tried to add userName=\"{userName}\" userId=\"{userId}\" as a trivia game controller for \"{twitchChannel}\", but this user has already been added as one')
            return AddTriviaGameControllerResult.ALREADY_EXISTS

        await connection.execute(
            '''
                INSERT INTO triviagamecontrollers (twitchchannel, userid)
                VALUES ($1, $2)
                ON CONFLICT (twitchchannel, userid) DO NOTHING
            ''',
            twitchChannel, userId
        )

        await connection.close()
        self.__timber.log('TriviaGameControllersRepository', f'Added userName=\"{userName}\" userId=\"{userId}\" as a trivia game controller for \"{twitchChannel}\"')

        return AddTriviaGameControllerResult.ADDED

    async def getControllers(self, twitchChannel: str) -> List[TriviaGameController]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT triviagamecontrollers.twitchchannel, triviagamecontrollers.userid, userids.username FROM triviagamecontrollers
                INNER JOIN userids ON triviagamecontrollers.userid = userids.userid
                WHERE triviagamecontrollers.twitchchannel = $1
                ORDER BY userids.username ASC
            ''',
            twitchChannel
        )

        controllers: List[TriviaGameController] = list()

        if not utils.hasItems(records):
            await connection.close()
            return controllers

        for record in records:
            controllers.append(TriviaGameController(
                twitchChannel = record[0],
                userId = record[1],
                userName = record[2]
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
                    CREATE TABLE IF NOT EXISTS triviagamecontrollers (
                        twitchchannel public.citext NOT NULL,
                        userid public.citext NOT NULL,
                        PRIMARY KEY (twitchchannel, userid)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS triviagamecontrollers (
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        userid TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (twitchchannel, userid)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def removeController(
        self,
        twitchChannel: str,
        userName: str
    ) -> RemoveTriviaGameControllerResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        userId: Optional[str] = None

        try:
            userId = await self.__userIdsRepository.fetchUserId(userName)
        except (RuntimeError, ValueError) as e:
            self.__timber.log('TriviaGameControllersRepository', f'Encountered exception when trying to remove \"{userName}\" as a trivia game controller for \"{twitchChannel}\": {e}', e)
            return RemoveTriviaGameControllerResult.ERROR

        if not utils.isValidStr(userId):
            self.__timber.log('TriviaGameControllersRepository', f'Retrieved no userId from UserIdsRepository when trying to remove \"{userName}\" as a trivia game controller for \"{twitchChannel}\"')
            return RemoveTriviaGameControllerResult.ERROR

        connection = await self.__backingDatabase.getConnection()
        await connection.execute(
            '''
                DELETE FROM triviagamecontrollers
                WHERE twitchchannel = $1 AND userid = $2
            ''',
            twitchChannel, userId
        )

        await connection.close()
        self.__timber.log('TriviaGameControllersRepository', f'Removed userName=\"{userName}\" userId=\"{userId}\" as a trivia game controller for \"{twitchChannel}\"')

        return RemoveTriviaGameControllerResult.REMOVED
