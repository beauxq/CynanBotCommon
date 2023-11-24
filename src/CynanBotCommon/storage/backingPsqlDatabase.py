from asyncio import AbstractEventLoop
from typing import Optional

import asyncpg

try:
    from CynanBotCommon.storage.backingDatabase import BackingDatabase
    from CynanBotCommon.storage.databaseConnection import DatabaseConnection
    from CynanBotCommon.storage.databaseType import DatabaseType
    from CynanBotCommon.storage.psqlCredentialsProvider import \
        PsqlCredentialsProvider
    from CynanBotCommon.storage.psqlDatabaseConnection import \
        PsqlDatabaseConnection
except:
    from storage.backingDatabase import BackingDatabase
    from storage.databaseConnection import DatabaseConnection
    from storage.databaseType import DatabaseType
    from storage.psqlCredentialsProvider import PsqlCredentialsProvider
    from storage.psqlDatabaseConnection import PsqlDatabaseConnection


class BackingPsqlDatabase(BackingDatabase):

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        psqlCredentialsProvider: PsqlCredentialsProvider
    ):
        if not isinstance(eventLoop, AbstractEventLoop):
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not isinstance(psqlCredentialsProvider, PsqlCredentialsProvider):
            raise ValueError(f'psqlCredentialsProvider argument is malformed: \"{psqlCredentialsProvider}\"')

        self.__eventLoop: AbstractEventLoop = eventLoop
        self.__psqlCredentialsProvider: PsqlCredentialsProvider = psqlCredentialsProvider

        self.__connectionPool: Optional[asyncpg.Pool] = None

    async def __createCollations(self, databaseConnection: DatabaseConnection):
        if not isinstance(databaseConnection, DatabaseConnection):
            raise ValueError(f'databaseConnection argument is malformed: \"{databaseConnection}\"')

        await databaseConnection.execute('CREATE EXTENSION IF NOT EXISTS citext')

    async def getConnection(self) -> DatabaseConnection:
        connectionPoolCreated = False

        if self.__connectionPool is None:
            connectionPoolCreated = True
            databaseName = await self.__psqlCredentialsProvider.requireDatabaseName()
            maxConnections = await self.__psqlCredentialsProvider.requireMaxConnections()
            password = await self.__psqlCredentialsProvider.getPassword()
            user = await self.__psqlCredentialsProvider.requireUser()

            self.__connectionPool = await asyncpg.create_pool(
                database = databaseName,
                loop = self.__eventLoop,
                max_size = maxConnections,
                password = password,
                user = user
            )

        connection = await self.__connectionPool.acquire()

        databaseConnection: DatabaseConnection = PsqlDatabaseConnection(
            connection = connection,
            pool = self.__connectionPool
        )

        if connectionPoolCreated:
            await self.__createCollations(databaseConnection)

        return databaseConnection

    def getDatabaseType(self) -> DatabaseType:
        return DatabaseType.POSTGRESQL
