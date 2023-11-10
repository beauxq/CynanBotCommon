import traceback
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.network.exceptions import GenericNetworkException
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
    from CynanBotCommon.twitch.twitchApiServiceInterface import \
        TwitchApiServiceInterface
    from CynanBotCommon.twitch.twitchUserDetails import TwitchUserDetails
    from CynanBotCommon.users.exceptions import NoSuchUserException
    from CynanBotCommon.users.userIdsRepositoryInterface import \
        UserIdsRepositoryInterface
except:
    import utils
    from network.exceptions import GenericNetworkException
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface

    from twitch.twitchApiServiceInterface import TwitchApiServiceInterface
    from twitch.twitchUserDetails import TwitchUserDetails
    from users.exceptions import NoSuchUserException
    from users.userIdsRepositoryInterface import UserIdsRepositoryInterface


class UserIdsRepository(UserIdsRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface,
        twitchApiService: TwitchApiServiceInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(twitchApiService, TwitchApiServiceInterface):
            raise ValueError(f'twitchApiService argument is malformed: \"{twitchApiService}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber
        self.__twitchApiService: TwitchApiServiceInterface = twitchApiService

        self.__isDatabaseReady: bool = False

    async def fetchAnonymousUserId(self, twitchAccessToken: str) -> Optional[str]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        # this is hardcoded to the ID of the "AnAnonymousGifter" account on Twitch
        return '274598607'

    async def fetchAnonymousUserName(self, twitchAccessToken: str) -> Optional[str]:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        anonymousUserId = await self.fetchAnonymousUserId()

        return await self.fetchUserName(
            userId = anonymousUserId,
            twitchAccessToken = twitchAccessToken
        )

    async def fetchUserId(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None
    ) -> Optional[str]:
        if not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')
        elif twitchAccessToken is not None and not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT userid FROM userids
                WHERE username = $1
                LIMIT 1
            ''',
            userName
        )

        userId: Optional[str] = None
        if utils.hasItems(record):
            userId = record[0]

        await connection.close()

        if utils.isValidStr(userId):
            return userId
        elif not utils.isValidStr(twitchAccessToken):
            self.__timber.log('UserIdsRepository', f'Can\'t lookup Twitch user ID for \"{userName}\" as no twitchAccessToken was specified')
            return None

        self.__timber.log('UserIdsRepository', f'User ID for username \"{userName}\" wasn\'t found locally, so performing a network call to fetch instead...')
        userDetails: Optional[TwitchUserDetails] = None

        try:
            userDetails = await self.__twitchApiService.fetchUserDetails(
                twitchAccessToken = twitchAccessToken,
                userName = userName
            )
        except GenericNetworkException as e:
            self.__timber.log('UserIdsRepository', f'Received a network error when fetching Twitch user ID for username \"{userName}\": {e}', e, traceback.format_exc())
            return None

        if userDetails is None:
            self.__timber.log('UserIdsRepository', f'Unable to retrieve Twitch user ID for username \"{userName}\"')
            return None

        userId = userDetails.getUserId()
        await self.setUser(userId = userId, userName = userName)

        return userId

    async def fetchUserIdAsInt(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None
    ) -> Optional[int]:
        userId = await self.fetchUserId(
            userName = userName,
            twitchAccessToken = twitchAccessToken
        )

        if not utils.isValidStr(userId):
            return None

        return int(userId)

    async def fetchUserName(
        self,
        userId: str,
        twitchAccessToken: Optional[str] = None
    ) -> Optional[str]:
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif twitchAccessToken is not None and not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT username FROM userids
                WHERE userid = $1
                LIMIT 1
            ''',
            userId
        )

        userName: Optional[str] = None
        if utils.hasItems(record):
            userName = record[0]

        await connection.close()

        if utils.isValidStr(userName):
            return userName
        elif not utils.isValidStr(twitchAccessToken):
            self.__timber.log('UserIdsRepository', f'Can\'t lookup Twitch username for \"{userId}\" as no twitchAccessToken was specified')
            return None

        self.__timber.log('UserIdsRepository', f'Username for user ID \"{userId}\" wasn\'t found locally, so performing a network call to fetch instead...')
        userDetails: Optional[TwitchUserDetails] = None

        try:
            userDetails = await self.__twitchApiService.fetchUserDetails(
                twitchAccessToken = twitchAccessToken,
                userName = userName
            )
        except GenericNetworkException as e:
            self.__timber.log('UserIdsRepository', f'Received a network error when fetching Twitch username for user ID \"{userId}\": {e}', e, traceback.format_exc())
            return None

        if userDetails is None:
            self.__timber.log('UserIdsRepository', f'Unable to retrieve Twitch username for user ID \"{userId}\"')
            return None

        userName = userDetails.getLogin()
        await self.setUser(userId = userId, userName = userName)

        return userName

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
                    CREATE TABLE IF NOT EXISTS userids (
                        userid public.citext NOT NULL PRIMARY KEY,
                        username public.citext NOT NULL
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS userids (
                        userid TEXT NOT NULL PRIMARY KEY COLLATE NOCASE,
                        username TEXT NOT NULL COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def requireAnonymousUserId(self, twitchAccessToken: str) -> str:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        anonymousUserId = await self.fetchAnonymousUserId(twitchAccessToken)

        if not utils.isValidStr(anonymousUserId):
            raise NoSuchUserException(f'Unable to fetch Twitch user ID for anonymous user')

        return anonymousUserId

    async def requireAnonymousUserName(self, twitchAccessToken: str) -> str:
        if not utils.isValidStr(twitchAccessToken):
            raise ValueError(f'twitchAccessToken argument is malformed: \"{twitchAccessToken}\"')

        anonymousUserName = await self.fetchAnonymousUserName(twitchAccessToken)

        if not utils.isValidStr(anonymousUserName):
            raise NoSuchUserException(f'Unable to fetch Twitch user name for anonymous user')

        return anonymousUserName

    async def requireUserId(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None
    ) -> str:
        userId = await self.fetchUserId(
            userName = userName,
            twitchAccessToken = twitchAccessToken
        )

        if not utils.isValidStr(userId):
            raise NoSuchUserException(f'Unable to fetch Twitch user ID for username \"{userName}\"')

        return userId

    async def requireUserIdAsInt(
        self,
        userName: str,
        twitchAccessToken: Optional[str] = None
    ) -> int:
        userIdStr = await self.fetchUserId(
            userName = userName,
            twitchAccessToken = twitchAccessToken
        )

        userIdInt: Optional[int] = None

        try:
            userIdInt = int(userIdStr)
        except:
            pass

        if not utils.isValidInt(userIdInt):
            raise NoSuchUserException(f'Unable to find Twitch user ID for username \"{userName}\"')

        return userIdInt

    async def requireUserName(
        self,
        userId: str,
        twitchAccessToken: Optional[str] = None
    ) -> str:
        userName = await self.fetchUserName(
            userId = userId,
            twitchAccessToken = twitchAccessToken
        )

        if not utils.isValidStr(userName):
            raise NoSuchUserException(f'Unable to fetch Twitch user name for user ID \"{userId}\"')

        return userName

    async def setUser(self, userId: str, userName: str):
        if not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO userids (userid, username)
                VALUES ($1, $2)
                ON CONFLICT (userid) DO UPDATE SET username = EXCLUDED.username
            ''',
            userId, userName
        )

        await connection.close()
