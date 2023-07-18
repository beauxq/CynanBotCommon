from datetime import datetime, timezone
from typing import Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.recurringActions.mostRecentRecurringAction import \
        MostRecentRecurringAction
    from CynanBotCommon.recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from CynanBotCommon.recurringActions.recurringAction import RecurringAction
    from CynanBotCommon.recurringActions.recurringActionType import \
        RecurringActionType
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.timber.timberInterface import TimberInterface
except:
    import utils
    from recurringActions.mostRecentRecurringAction import \
        MostRecentRecurringAction
    from recurringActions.mostRecentRecurringActionRepositoryInterface import \
        MostRecentRecurringActionRepositoryInterface
    from recurringActions.recurringAction import RecurringAction
    from recurringActions.recurringActionType import RecurringActionType
    from simpleDateTime import SimpleDateTime
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from timber.timberInterface import TimberInterface


class MostRecentRecurringActionRepository(MostRecentRecurringActionRepositoryInterface):

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        timber: TimberInterface,
        timeZone: timezone = timezone.utc
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(timber, TimberInterface):
            raise ValueError(f'timber argument is malformed: \"{timber}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__timber: TimberInterface = timber
        self.__timeZone: timezone = timeZone

        self.__isDatabaseReady: bool = False

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
                    CREATE TABLE IF NOT EXISTS mostrecentrecurringaction (
                        actiontype text NOT NULL,
                        datetime text NOT NULL,
                        twitchchannel public.citext NOT NULL PRIMARY KEY
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS mostrecentrecurringaction (
                        actiontype TEXT NOT NULL,
                        datetime TEXT NOT NULL,
                        twitchchannel TEXT NOT NULL PRIMARY KEY COLLATE NOCASE
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()

    async def getMostRecentRecurringAction(
        self,
        twitchChannel: str
    ) -> Optional[MostRecentRecurringAction]:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT actiontype, datetime FROM mostrecentrecurringaction
                WHERE twitchchannel = $1
                LIMIT 1
            ''',
            twitchChannel
        )

        await connection.close()

        if not utils.hasItems(record):
            return None

        actionType = RecurringActionType.fromStr(record[0])
        simpleDateTime = SimpleDateTime(utils.getDateTimeFromStr(record[1]))

        return MostRecentRecurringAction(
            actionType = actionType,
            simpleDateTime = simpleDateTime,
            twitchChannel = twitchChannel
        )

    async def setMostRecentRecurringAction(self, action: RecurringAction):
        if not isinstance(action, RecurringAction):
            raise ValueError(f'action argument is malformed: \"{action}\"')

        nowDateTime = datetime.now(self.__timeZone)
        nowDateTimeStr = nowDateTime.isoformat()

        connection = await self.__getDatabaseConnection()
        await connection.execute(
            '''
                INSERT INTO mostrecentrecurringaction (actiontype, datetime, twitchchannel)
                VALUES ($1, $2, $3)
                ON CONFLICT (twitchchannel) DO UPDATE SET actiontype = EXCLUDED.actiontype, datetime = EXCLUDED.datetime
            ''',
            action.getActionType().toStr(), nowDateTimeStr, action.getTwitchChannel()
        )

        await connection.close()

        self.__timber.log('MostRecentRecurringActionRepository', f'Updated \"{action.getActionType()}\" for \"{action.getTwitchChannel()}\" ({nowDateTimeStr})')
