from typing import List, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.cuteness.cutenessChampionsResult import \
        CutenessChampionsResult
    from CynanBotCommon.cuteness.cutenessDate import CutenessDate
    from CynanBotCommon.cuteness.cutenessEntry import CutenessEntry
    from CynanBotCommon.cuteness.cutenessHistoryEntry import \
        CutenessHistoryEntry
    from CynanBotCommon.cuteness.cutenessHistoryResult import \
        CutenessHistoryResult
    from CynanBotCommon.cuteness.cutenessLeaderboardEntry import \
        CutenessLeaderboardEntry
    from CynanBotCommon.cuteness.cutenessLeaderboardHistoryResult import \
        CutenessLeaderboardHistoryResult
    from CynanBotCommon.cuteness.cutenessLeaderboardResult import \
        CutenessLeaderboardResult
    from CynanBotCommon.cuteness.cutenessResult import CutenessResult
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.users.userIdsRepository import UserIdsRepository
except:
    import utils
    from cuteness.cutenessChampionsResult import CutenessChampionsResult
    from cuteness.cutenessDate import CutenessDate
    from cuteness.cutenessEntry import CutenessEntry
    from cuteness.cutenessHistoryEntry import CutenessHistoryEntry
    from cuteness.cutenessHistoryResult import CutenessHistoryResult
    from cuteness.cutenessLeaderboardEntry import CutenessLeaderboardEntry
    from cuteness.cutenessLeaderboardHistoryResult import \
        CutenessLeaderboardHistoryResult
    from cuteness.cutenessLeaderboardResult import CutenessLeaderboardResult
    from cuteness.cutenessResult import CutenessResult
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType

    from users.userIdsRepository import UserIdsRepository


class CutenessRepository():

    def __init__(
        self,
        backingDatabase: BackingDatabase,
        userIdsRepository: UserIdsRepository,
        historyLeaderboardSize: int = 3,
        historySize: int = 5,
        leaderboardSize: int = 10
    ):
        if not isinstance(backingDatabase, BackingDatabase):
            raise ValueError(f'backingDatabase argument is malformed: \"{backingDatabase}\"')
        elif not isinstance(userIdsRepository, UserIdsRepository):
            raise ValueError(f'userIdsRepository argument is malformed: \"{userIdsRepository}\"')
        elif not utils.isValidInt(historyLeaderboardSize):
            raise ValueError(f'historyLeaderboardSize argument is malformed: \"{historyLeaderboardSize}\"')
        elif historyLeaderboardSize < 2 or historyLeaderboardSize > 6:
            raise ValueError(f'historyLeaderboardSize argument is out of bounds: {historyLeaderboardSize}')
        elif not utils.isValidInt(historySize):
            raise ValueError(f'historySize argument is malformed: \"{historySize}\"')
        elif historySize < 2 or historySize > 12:
            raise ValueError(f'historySize argument is out of bounds: {historySize}')
        elif not utils.isValidInt(leaderboardSize):
            raise ValueError(f'leaderboardSize argument is malformed: \"{leaderboardSize}\"')
        elif leaderboardSize < 3 or leaderboardSize > 10:
            raise ValueError(f'leaderboardSize argument is out of bounds: {leaderboardSize}')

        self.__backingDatabase: BackingDatabase = backingDatabase
        self.__userIdsRepository: UserIdsRepository = userIdsRepository
        self.__historyLeaderboardSize: int = historyLeaderboardSize
        self.__historySize: int = historySize
        self.__leaderboardSize: int = leaderboardSize

        self.__isDatabaseReady: bool = False

    async def fetchCuteness(
        self,
        twitchChannel: str,
        userId: str,
        userName: str,
    ) -> CutenessResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        await self.__userIdsRepository.setUser(userId = userId, userName = userName)

        cutenessDate = CutenessDate()

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT cuteness.cuteness, cuteness.userid, userids.username FROM cuteness
                INNER JOIN userids ON cuteness.userid = userids.userid
                WHERE cuteness.twitchchannel = $1 AND cuteness.userid = $2 AND cuteness.utcyearandmonth = $3
                LIMIT 1
            ''',
            twitchChannel, userId, cutenessDate.getStr()
        )

        if not utils.hasItems(record):
            await connection.close()
            return CutenessResult(
                cutenessDate = cutenessDate,
                cuteness = 0,
                userId = userId,
                userName = userName
            )

        cuteness: int = record[0]
        await connection.close()

        return CutenessResult(
            cutenessDate = cutenessDate,
            cuteness = cuteness,
            userId = userId,
            userName = userName
        )

    async def fetchCutenessChampions(self, twitchChannel: str) -> CutenessChampionsResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT cuteness.userid, userids.username, SUM(cuteness.cuteness) AS totalcuteness FROM cuteness
                INNER JOIN userids ON cuteness.userid = userids.userid where cuteness.twitchchannel = $1 AND cuteness.userid != $2
                GROUP BY cuteness.userid, userids.username
                ORDER BY totalcuteness DESC
                LIMIT $3
            ''',
            twitchChannel, twitchChannelUserId, self.__leaderboardSize
        )

        await connection.close()

        if not utils.hasItems(records):
            return CutenessChampionsResult(twitchChannel = twitchChannel)

        champions: List[CutenessLeaderboardEntry] = list()

        for index, record in enumerate(records):
            print(f'TEMP STUPID THING: #{index} {record[0]} ({type(record[0])}); {record[1]} ({type(record[1])}); {record[2]} ({type(record[2])})')
            champions.append(CutenessLeaderboardEntry(
                cuteness = record[2],
                rank = index + 1,
                userId = record[0],
                userName = record[1]
            ))

        return CutenessChampionsResult(
            twitchChannel = twitchChannel,
            champions = champions
        )

    async def fetchCutenessHistory(
        self,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> CutenessHistoryResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        await self.__userIdsRepository.setUser(userId = userId, userName = userName)

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT cuteness, utcyearandmonth FROM cuteness
                WHERE twitchchannel = $1 AND userid = $2 AND cuteness IS NOT NULL AND cuteness >= 1
                ORDER BY utcyearandmonth DESC
                LIMIT $3
            ''',
            twitchChannel, userId, self.__historySize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessHistoryResult(
                userId = userId,
                userName = userName
            )

        entries: List[CutenessHistoryEntry] = list()

        for record in records:
            entries.append(CutenessHistoryEntry(
                cutenessDate = CutenessDate(record[1]),
                cuteness = record[0],
                userId = userId,
                userName = userName
            ))

        # sort entries into newest to oldest order
        entries.sort(key = lambda entry: entry.getCutenessDate(), reverse = True)

        record = await connection.fetchRow(
            '''
                SELECT SUM(cuteness) FROM cuteness
                WHERE twitchchannel = $1 AND userid = $2 AND cuteness IS NOT NULL AND cuteness >= 1
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        totalCuteness: int = 0

        if utils.hasItems(record):
            # this should be impossible at this point, but let's just be safe
            totalCuteness = record[0]

        record = await connection.fetchRow(
            '''
                SELECT cuteness, utcyearandmonth FROM cuteness
                WHERE twitchchannel = $1 AND userid = $2 AND cuteness IS NOT NULL AND cuteness >= 1
                ORDER BY cuteness DESC
                LIMIT 1
            ''',
            twitchChannel, userId
        )

        bestCuteness: Optional[CutenessHistoryEntry] = None

        if utils.hasItems(record):
            # again, this should be impossible here, but let's just be safe
            bestCuteness = CutenessHistoryEntry(
                cutenessDate = CutenessDate(record[1]),
                cuteness = record[0],
                userId = userId,
                userName = userName
            )

        await connection.close()

        return CutenessHistoryResult(
            userId = userId,
            userName = userName,
            bestCuteness = bestCuteness,
            totalCuteness = totalCuteness,
            entries = entries
        )

    async def fetchCutenessIncrementedBy(
        self,
        incrementAmount: int,
        twitchChannel: str,
        userId: str,
        userName: str
    ) -> CutenessResult:
        if not utils.isValidInt(incrementAmount):
            raise ValueError(f'incrementAmount argument is malformed: \"{incrementAmount}\"')
        elif incrementAmount < utils.getLongMinSafeSize() or incrementAmount > utils.getLongMaxSafeSize():
            raise ValueError(f'incrementAmount argument is out of bounds: {incrementAmount}')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif userId == '0':
            raise ValueError(f'userId argument is an illegal value: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        await self.__userIdsRepository.setUser(userId = userId, userName = userName)

        cutenessDate = CutenessDate()

        connection = await self.__getDatabaseConnection()
        record = await connection.fetchRow(
            '''
                SELECT cuteness FROM cuteness
                WHERE twitchchannel = $1 AND userid = $2 AND utcyearandmonth = $3
                LIMIT 1
            ''',
            twitchChannel, userId, cutenessDate.getStr()
        )

        oldCuteness: int = 0

        if utils.hasItems(record):
            oldCuteness = record[0]

        newCuteness: int = oldCuteness + incrementAmount

        if newCuteness < 0:
            newCuteness = 0
        elif newCuteness > utils.getLongMaxSafeSize():
            raise OverflowError(f'New cuteness ({newCuteness}) would be too large (old cuteness = {oldCuteness}) (increment amount = {incrementAmount})')

        await connection.execute(
            '''
                INSERT INTO cuteness (cuteness, twitchchannel, userid, utcyearandmonth)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (twitchchannel, userid, utcyearandmonth) DO UPDATE SET cuteness = EXCLUDED.cuteness
            ''',
            newCuteness, twitchChannel, userId, cutenessDate.getStr()
        )

        await connection.close()

        return CutenessResult(
            cutenessDate = cutenessDate,
            cuteness = newCuteness,
            userId = userId,
            userName = userName
        )

    async def fetchCutenessLeaderboard(
        self,
        twitchChannel: str,
        specificLookupUserId: Optional[str] = None,
        specificLookupUserName: Optional[str] = None
    ) -> CutenessLeaderboardResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        cutenessDate = CutenessDate()
        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT cuteness.cuteness, cuteness.userid, userids.username FROM cuteness
                INNER JOIN userids ON cuteness.userid = userids.userid
                WHERE cuteness.twitchchannel = $1 AND cuteness.utcyearandmonth = $2 AND cuteness.cuteness IS NOT NULL AND cuteness.cuteness >= 1 AND cuteness.userid != $3
                ORDER BY cuteness.cuteness DESC
                LIMIT $4
            ''',
            twitchChannel, cutenessDate.getStr(), twitchChannelUserId, self.__leaderboardSize
        )

        await connection.close()

        if not utils.hasItems(records):
            return CutenessLeaderboardResult(cutenessDate = cutenessDate)

        entries: List[CutenessLeaderboardEntry] = list()

        for index, record in enumerate(records):
            entries.append(CutenessLeaderboardEntry(
                cuteness = record[0],
                rank = index + 1,
                userId = record[1],
                userName = record[2]
            ))

        specificLookupAlreadyInResults: bool = False
        if utils.isValidStr(specificLookupUserId) or utils.isValidStr(specificLookupUserName):
            for entry in entries:
                if utils.isValidStr(specificLookupUserId) and entry.getUserId().lower() == specificLookupUserId.lower():
                    specificLookupAlreadyInResults = True
                    break
                elif utils.isValidStr(specificLookupUserName) and entry.getUserName().lower() == specificLookupUserName.lower():
                    specificLookupAlreadyInResults = True
                    break

        specificLookupCutenessResult: Optional[CutenessResult] = None
        if not specificLookupAlreadyInResults and (utils.isValidStr(specificLookupUserId) or utils.isValidStr(specificLookupUserName)):
            if not utils.isValidStr(specificLookupUserId):
                try:
                    specificLookupUserId = await self.__userIdsRepository.fetchUserId(userName = specificLookupUserName)
                except ValueError:
                    # this exception can be safely ignored
                    pass
            else:
                try:
                    specificLookupUserName = await self.__userIdsRepository.fetchUserName(specificLookupUserId)
                except (RuntimeError, ValueError):
                    # this exception can be safely ignored
                    pass

            if utils.isValidStr(specificLookupUserId) and utils.isValidStr(specificLookupUserName):
                specificLookupCutenessResult = await self.fetchCuteness(
                    twitchChannel = twitchChannel,
                    userId = specificLookupUserId,
                    userName = specificLookupUserName
                )

        return CutenessLeaderboardResult(
            cutenessDate = cutenessDate,
            entries = entries,
            specificLookupCutenessResult = specificLookupCutenessResult
        )

    async def fetchCutenessLeaderboardHistory(self, twitchChannel: str) -> CutenessLeaderboardHistoryResult:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        twitchChannelUserId = await self.__userIdsRepository.fetchUserId(userName = twitchChannel)

        connection = await self.__getDatabaseConnection()
        records = await connection.fetchRows(
            '''
                SELECT DISTINCT utcyearandmonth FROM cuteness
                WHERE twitchchannel = $1 AND utcyearandmonth != $2
                ORDER BY utcyearandmonth DESC
                LIMIT $3
            ''',
            twitchChannel, CutenessDate().getStr(), self.__historyLeaderboardSize
        )

        if not utils.hasItems(records):
            await connection.close()
            return CutenessLeaderboardHistoryResult(twitchChannel = twitchChannel)

        leaderboards: List[CutenessLeaderboardResult] = list()

        for record in records:
            cutenessDate = CutenessDate(record[0])
            monthRecords = await connection.fetchRows(
                '''
                    SELECT cuteness.cuteness, cuteness.userid, userids.username FROM cuteness
                    INNER JOIN userids ON cuteness.userid = userids.userid
                    WHERE cuteness.cuteness IS NOT NULL AND cuteness.cuteness >= 1 AND cuteness.twitchchannel = $1 AND cuteness.userid != $2 AND cuteness.utcyearandmonth = $3
                    ORDER BY cuteness.cuteness DESC
                    LIMIT $4
                ''',
                twitchChannel, twitchChannelUserId, cutenessDate.getStr(), self.__historyLeaderboardSize
            )

            if not utils.hasItems(monthRecords):
                continue

            entries: List[CutenessLeaderboardEntry] = list()
            rank: int = 1

            for monthRecord in monthRecords:
                entries.append(CutenessLeaderboardEntry(
                    cuteness = monthRecord[0],
                    rank = rank,
                    userId = monthRecord[1],
                    userName = monthRecord[2]
                ))
                rank = rank + 1

            leaderboards.append(CutenessLeaderboardResult(
                cutenessDate = cutenessDate,
                entries = entries
            ))

        await connection.close()

        return CutenessLeaderboardHistoryResult(
            twitchChannel = twitchChannel,
            leaderboards = leaderboards
        )

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
                    CREATE TABLE IF NOT EXISTS cuteness (
                        cuteness bigint DEFAULT 0 NOT NULL,
                        twitchchannel public.citext NOT NULL,
                        userid public.citext NOT NULL,
                        utcyearandmonth public.citext NOT NULL,
                        PRIMARY KEY (twitchchannel, userid, utcyearandmonth)
                    )
                '''
            )
        elif connection.getDatabaseType() is DatabaseType.SQLITE:
            await connection.createTableIfNotExists(
                '''
                    CREATE TABLE IF NOT EXISTS cuteness (
                        cuteness INTEGER NOT NULL DEFAULT 0,
                        twitchchannel TEXT NOT NULL COLLATE NOCASE,
                        userid TEXT NOT NULL COLLATE NOCASE,
                        utcyearandmonth TEXT NOT NULL COLLATE NOCASE,
                        PRIMARY KEY (twitchchannel, userid, utcyearandmonth)
                    )
                '''
            )
        else:
            raise RuntimeError(f'Encountered unexpected DatabaseType when trying to create tables: \"{connection.getDatabaseType()}\"')

        await connection.close()
