import asyncio
import queue
from asyncio import AbstractEventLoop
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, List, Optional

import aiofiles
import aiofiles.os
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.timber.timberEntry import TimberEntry
except:
    import utils
    from timber.timberEntry import TimberEntry


class Timber():

    def __init__(
        self,
        eventLoop: AbstractEventLoop,
        alsoPrintToStandardOut: bool = True,
        sleepTimeSeconds: float = 10,
        timberRootDirectory: str = 'CynanBotCommon/timber'
    ):
        if not isinstance(eventLoop, AbstractEventLoop):
            raise ValueError(f'eventLoop argument is malformed: \"{eventLoop}\"')
        elif not utils.isValidBool(alsoPrintToStandardOut):
            raise ValueError(f'alsoPrintToStandardOut argument is malformed: \"{alsoPrintToStandardOut}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 1 or sleepTimeSeconds > 60:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidStr(timberRootDirectory):
            raise ValueError(f'timberRootDirectory argument is malformed: \"{timberRootDirectory}\"')

        self.__alsoPrintToStandardOut: bool = alsoPrintToStandardOut
        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__timberRootDirectory: str = timberRootDirectory

        self.__entryQueue: SimpleQueue[TimberEntry] = SimpleQueue()
        eventLoop.create_task(self.__startEventLoop())

    def __getErrorStatement(self, exception: Exception) -> str:
        if not isinstance(exception, Exception):
            raise ValueError(f'exception argument is malformed: \"{exception}\"')

        return f'{exception}\n'

    def __getLogStatement(self, ensureNewLine: bool, timberEntry: TimberEntry) -> str:
        if not utils.isValidBool(ensureNewLine):
            raise ValueError(f'ensureNewLine argument is malformed: \"{ensureNewLine}\"')
        elif not isinstance(timberEntry, TimberEntry):
            raise ValueError(f'timberEntry argument is malformed: \"{timberEntry}\"')

        logStatement = f'{timberEntry.getSimpleDateTime().getDateAndTimeStr()} — {timberEntry.getTag()} — {timberEntry.getMsg()}'
        logStatement = logStatement.strip()

        if ensureNewLine:
            logStatement = f'{logStatement}\n'

        return logStatement

    def log(self, tag: str, msg: str, exception: Optional[Exception] = None):
        if not utils.isValidStr(tag):
            raise ValueError(f'tag argument is malformed: \"{tag}\"')
        elif not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')
        elif exception is not None and not isinstance(exception, Exception):
            raise ValueError(f'exception argument is malformed: \"{exception}\"')

        timberEntry = TimberEntry(
            tag = tag,
            msg = msg,
            exception = exception
        )

        if self.__alsoPrintToStandardOut:
            print(self.__getLogStatement(False, timberEntry))

        self.__entryQueue.put(timberEntry)

    async def __startEventLoop(self):
        while True:
            entries: List[TimberEntry] = list()

            try:
                while not self.__entryQueue.empty():
                    entry = self.__entryQueue.get_nowait()
                    entries.append(entry)
            except queue.Empty:
                pass

            await self.__writeToLogFiles(entries)
            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __writeToLogFiles(self, entries: List[TimberEntry]):
        if len(entries) == 0:
            return

        # The logic below is kind of intense, but we do this in order to favor logical complexity
        # in exchange for I/O simplicity. By doing things this way, we only need to attempt to
        # create folders once, files once, and we also just open a file handle one time too.

        # This dictionary stores a directory, and then a list of files, and then the contents to
        # write into the files themselves. This dictionary does not make any attempt at handling
        # error logging.
        structure: Dict[str, Dict[str, List[TimberEntry]]] = defaultdict(lambda: defaultdict(lambda: list()))

        # This dictionary is used for error logging, and just like the dictionary above, stores
        # a directory, and then a list of files, and then the contents to write into the files
        # themselves.
        errorStructure: Dict[str, Dict[str, List[TimberEntry]]] = defaultdict(lambda: defaultdict(lambda: list()))

        for entry in entries:
            simpleDateTime = entry.getSimpleDateTime()
            timberDirectory = f'{self.__timberRootDirectory}/{simpleDateTime.getYearStr()}/{simpleDateTime.getMonthStr()}'
            timberFile = f'{timberDirectory}/{simpleDateTime.getDayStr()}.log'
            structure[timberDirectory][timberFile].append(entry)

            if entry.hasException():
                timberErrorDirectory = f'{timberDirectory}/errors'
                timberErrorFile = f'{timberErrorDirectory}/{simpleDateTime.getDayStr()}.log'
                errorStructure[timberErrorDirectory][timberErrorFile].append(entry)

        for timberDirectory, timberFileToEntriesDict in structure.items():
            if not await aiofiles.ospath.exists(timberDirectory):
                await aiofiles.os.makedirs(timberDirectory)

            for timberFile, entriesList in timberFileToEntriesDict.items():
                async with aiofiles.open(timberFile, mode = 'a') as file:
                    for entry in entriesList:
                        logStatement = self.__getLogStatement(True, entry)
                        await file.write(logStatement)

        for timberErrorDirectory, timberErrorFileToEntriesDict in errorStructure.items():
            if not await aiofiles.ospath.exists(timberErrorDirectory):
                await aiofiles.os.makedirs(timberErrorDirectory)

            for timberErrorFile, entriesList in timberErrorFileToEntriesDict.items():
                async with aiofiles.open(timberErrorFile, mode = 'a') as file:
                    for entry in entriesList:
                        errorStatement = self.__getErrorStatement(entry.getException())
                        await file.write(errorStatement)
