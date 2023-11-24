from typing import Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.supStreamer.supStreamerAction import SupStreamerAction
    from CynanBotCommon.supStreamer.supStreamerChatter import \
        SupStreamerChatter
    from CynanBotCommon.supStreamer.supStreamerRepositoryInterface import \
        SupStreamerRepositoryInterface
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from simpleDateTime import SimpleDateTime
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from supStreamer.supStreamerAction import SupStreamerAction
    from supStreamer.supStreamerChatter import SupStreamerChatter
    from supStreamer.supStreamerRepositoryInterface import \
        SupStreamerRepositoryInterface
    from timber.timberInterface import TimberInterface


class SupStreamerRepository(SupStreamerRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber

        self.__cache: Dict[str, Optional[SupStreamerAction]] = dict()
        self.__isDatabaseReady: bool = False

    async def clearCaches(self):
        self.__cache.clear()
        self.__timber.log('SupStreamerRepository', 'Caches cleared')

    async def get(self, twitchChannelId: str) -> Optional[SupStreamerAction]:
        if not utils.isValidStr(twitchChannelId):
            raise ValueError(f'twitchChannelId argument is malformed: \"{twitchChannelId}\"')

        if twitchChannelId in self.__cache:
            return self.__cache[twitchChannelId]

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT supstreamerchatters.mostrecentsup, supstreamerchatters.chatteruserid, userids.username FROM supstreamerchatters
                INNER JOIN userids ON supstreamerchatters.twitchchannelid = userids.userid
                ORDER BY supstreamerchatters.mostrecentsup ASC
                WHERE supstreamerchatters.twitchchannelid = $1
            ''',
            twitchChannelId
        )

        await connection.close()
        twitchChannelName: Optional[str] = None
        chatters: Dict[str, Optional[SupStreamerChatter]] = dict()

        if utils.hasItems(records):
            for record in records:
                mostRecentSup: Optional[SimpleDateTime] = None

                if utils.isValidStr(record[0]):
                    mostRecentSup = SimpleDateTime(utils.getDateTimeFromStr(mostRecentSup))

                chatterUserId: str = record[1]

                chatters[chatterUserId] = SupStreamerChatter(
                    mostRecentSup = mostRecentSup,
                    userId = chatterUserId
                )

                if not utils.isValidStr(twitchChannelName):
                    twitchChannelName = record[2]

        action: Optional[SupStreamerAction] = None

        if utils.isValidStr(twitchChannelName):
            action = SupStreamerAction(
                chatters = chatters,
                broadcasterUserId = twitchChannelId,
                broadcasterUserName = twitchChannelName
            )

        self.__cache[twitchChannelId] = action
        return action

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
                    CREATE TABLE IF NOT EXISTS supstreamerchatters (
                        mostrecentsup text NOT NULL,
                        chatteruserid public.citext NOT NULL,
                        twitchchannelid public.citext NOT NULL
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS supstreamerchatters (
                        mostrecentsup TEXT NOT NULL,
                        chatteruserid TEXT NOT NULL COLLATE NOCASE,
                        twitchchannelid TEXT NOT NULL COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def update(self, chatterUserId: str, twitchChannelId: str):
        if not utils.isValidStr(chatterUserId):
            raise ValueError(f'chatterUserId argument is malformed: \"{chatterUserId}\"')
        elif not utils.isValidStr(twitchChannelId):
            raise ValueError(f'twitchChannelId argument is malformed: \"{twitchChannelId}\"')

        now = SimpleDateTime()

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO supstreamerchatters (mostrecentsup, chatteruserid, twitchchannelid)
                VALUES ($1, $2, $3)
                ON CONFLICT (mostrecentsup, chatteruserid, twitchchannelid) DO UPDATE SET mostrecentsup = EXCLUDED.mostrecentsup
            ''',
            now.getIsoFormatStr(), chatterUserId, twitchChannelId
        )

        await connection.close()
        action = await self.get(twitchChannelId)

        if action is None:
            return

        action.updateChatter(SupStreamerChatter(
            mostRecentSup = now,
            userId = chatterUserId
        ))
