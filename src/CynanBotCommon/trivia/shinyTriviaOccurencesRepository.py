from datetime import datetime, timezone
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.trivia.shinyTriviaResult import ShinyTriviaResult
except:
    import utils
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from trivia.shinyTriviaResult import ShinyTriviaResult


class ShinyTriviaOccurencesRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timeZone: timezone = timeZone

        self.__isDatabaseReady: bool = False

    async def fetchDetails(
        self,
        twitchChannel: str,
        userId: str
    ) -> ShinyTriviaResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT count, mostrecent FROM shinytriviaoccurences
                WHERE twitchchannel = $1 AND userid = $2
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        shinyCount: int = 0
        mostRecent: Optional[datetime] = None

        if utils.hasItems(record):
            shinyCount = record[0]
            mostRecent = utils.getDateTimeFromStr(record[1])

        await connection.close()

        return ShinyTriviaResult(
            mostRecent = mostRecent,
            newShinyCount = shinyCount,
            oldShinyCount = shinyCount,
            twitchChannel = twitchChannel,
            userId = userId
        )

    async def __getDatabaseConnection(self) -> DatabaseConnection:
        await self.__initDatabaseTable()
        return await self.__backingDatabase.getConnection()

    async def incrementShinyCount(
        self,
        twitchChannel: str,
        userId: str
    ) -> ShinyTriviaResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        result = await self.fetchDetails(
            twitchChannel = twitchChannel,
            userId = userId
        )

        newShinyCount: int = result.getOldShinyCount() + 1

        newResult = ShinyTriviaResult(
            mostRecent = datetime.now(self.__timeZone),
            newShinyCount = newShinyCount,
            oldShinyCount = result.getOldShinyCount(),
            twitchChannel = result.getTwitchChannel(),
            userId = result.getUserId()
        )

        await self.__updateShinyCount(
            newShinyCount = newResult.getNewShinyCount(),
            twitchChannel = newResult.getTwitchChannel(),
            userId = newResult.getUserId()
        )

        return newResult

    async def __initDatabaseTable(self):
        if self.__isDatabaseReady:
            return

        self.__isDatabaseReady = True
        connection = await self.__backingDatabase.getConnection()

        if connection.getDatabaseType() is DatabaseType.POSTGRESQL:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS shinytriviaoccurences (
                        count integer DEFAULT 0 NOT NULL,
                        mostrecent text NOT NULL,
                        twitchchannel public.citext NOT NULL,
                        userid public.citext NOT NULL,
                        PRIMARY KEY (twitchchannel, userid)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS shinytriviaoccurences (
                        count INTEGER NOT NULL DEFAULT 0,
                        mostrecent TEXT NOT NULL,
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        userid TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (twitchchannel, userid)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def __updateShinyCount(
        self,
        newShinyCount: int,
        twitchChannel: str,
        userId: str
    ):
        if not utils.isValidInt(newShinyCount):
            raise ValueError(f'newShinyCount argument is malformed: \"{newShinyCount}\"')
        elif newShinyCount < 0 or newShinyCount > utils.getIntMaxSafeSize():
            raise ValueError(f'newShinyCount argument is out of bounds: {newShinyCount}')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')

        nowDateTime = datetime.now(self.__timeZone)
        nowDateTimeStr = nowDateTime.isoformat()

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO shinytriviaoccurences (count, mostrecent, twitchchannel, userid)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (twitchchannel, userid) DO UPDATE SET count = EXCLUDED.count, mostrecent = EXCLUDED.mostrecent
            ''',
            newShinyCount, nowDateTimeStr, twitchChannel, userId
        )

        await connection.close()
