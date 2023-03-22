import asyncio
import queue
from collections import defaultdict
from queue import SimpleQueue
from typing import Dict, List

import aiofiles
import aiofiles.os
import aiofiles.ospath

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.backgroundTaskHelper import BackgroundTaskHelper
    from CynanBotCommon.chatLogger.absChatMessage import AbsChatMessage
    from CynanBotCommon.chatLogger.chatEventType import ChatEventType
    from CynanBotCommon.chatLogger.chatMessage import ChatMessage
    from CynanBotCommon.chatLogger.raidMessage import RaidMessage
except:
    import utils
    from backgroundTaskHelper import BackgroundTaskHelper
    from chatLogger.absChatMessage import AbsChatMessage
    from chatLogger.chatEventType import ChatEventType
    from chatLogger.chatMessage import ChatMessage
    from chatLogger.raidMessage import RaidMessage


class ChatLogger():

    def __init__(
        self,
        backgroundTaskHelper: BackgroundTaskHelper,
        sleepTimeSeconds: float = 15,
        logRootDirectory: str = 'CynanBotCommon/chatLogger'
    ):
        if not isinstance(backgroundTaskHelper, BackgroundTaskHelper):
            raise ValueError(f'backgroundTaskHelper argument is malformed: \"{backgroundTaskHelper}\"')
        elif not utils.isValidNum(sleepTimeSeconds):
            raise ValueError(f'sleepTimeSeconds argument is malformed: \"{sleepTimeSeconds}\"')
        elif sleepTimeSeconds < 1 or sleepTimeSeconds > 60:
            raise ValueError(f'sleepTimeSeconds argument is out of bounds: {sleepTimeSeconds}')
        elif not utils.isValidStr(logRootDirectory):
            raise ValueError(f'logRootDirectory argument is malformed: \"{logRootDirectory}\"')

        self.__sleepTimeSeconds: float = sleepTimeSeconds
        self.__logRootDirectory: str = logRootDirectory

        self.__messageQueue: SimpleQueue[AbsChatMessage] = SimpleQueue()
        backgroundTaskHelper.createTask(self.__startMessageLoop())

    def __getLogStatement(self, message: AbsChatMessage) -> str:
        if not isinstance(message, AbsChatMessage):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        logStatement: str = f'{message.getSimpleDateTime().getDateAndTimeStr(True)} —'

        if message.getChatEventType() is ChatEventType.MESSAGE:
            chatMessage: ChatMessage = message
            logStatement = f'{logStatement} {chatMessage.getUserName()} ({chatMessage.getUserId()}) — {chatMessage.getMsg()}'
        elif message.getChatEventType() is ChatEventType.RAID:
            raidMessage: RaidMessage = message
            logStatement = f'{logStatement} Received raid from {raidMessage.getFromWho()} of {raidMessage.getRaidSizeStr()}!'
        else:
            raise RuntimeError(f'AbsChatMessage has unknown ChatEventType: \"{message.getChatEventType()}\"')

        return f'{logStatement.strip()}\n'

    def logMessage(self, msg: str, twitchChannel: str, userId: str, userName: str):
        if not utils.isValidStr(msg):
            raise ValueError(f'msg argument is malformed: \"{msg}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')
        elif not utils.isValidStr(userName):
            raise ValueError(f'userName argument is malformed: \"{userName}\"')

        chatMessage: AbsChatMessage = ChatMessage(
            msg = msg,
            twitchChannel = twitchChannel,
            userId = userId,
            userName = userName
        )

        self.__messageQueue.put(chatMessage)

    def logRaid(self, raidSize: int, fromWho: str, twitchChannel: str):
        if not utils.isValidInt(raidSize):
            raise ValueError(f'raidSize argument is malformed: \"{raidSize}\"')
        elif raidSize < 0:
            raise ValueError(f'raidSize argument is out of bounds: {raidSize}')
        elif not utils.isValidStr(fromWho):
            raise ValueError(f'fromWho argument is malformed: \"{fromWho}\"')
        elif not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        raidMessage: AbsChatMessage = RaidMessage(
            raidSize = raidSize,
            fromWho = fromWho,
            twitchChannel = twitchChannel
        )

        self.__messageQueue.put(raidMessage)

    async def __startMessageLoop(self):
        while True:
            messages: List[AbsChatMessage] = list()

            try:
                while not self.__messageQueue.empty():
                    message = self.__messageQueue.get_nowait()
                    messages.append(message)
            except queue.Empty:
                pass

            await self.__writeToLogFiles(messages)
            await asyncio.sleep(self.__sleepTimeSeconds)

    async def __writeToLogFiles(self, messages: List[AbsChatMessage]):
        if len(messages) == 0:
            return

        # The below logic is kind of intense, however, there is a very similar/nearly identical
        # flow within the Timber class. Check that out for more information and context.

        structure: Dict[str, Dict[str, List[AbsChatMessage]]] = defaultdict(lambda: defaultdict(lambda: list()))

        for message in messages:
            twitchChannel = message.getTwitchChannel().lower()
            simpleDateTime = message.getSimpleDateTime()
            messageDirectory = f'{self.__logRootDirectory}/{twitchChannel}/{simpleDateTime.getYearStr()}/{simpleDateTime.getMonthStr()}'
            messageFile = f'{messageDirectory}/{simpleDateTime.getDayStr()}.log'
            structure[messageDirectory][messageFile].append(message)

        for messageDirectory, messageFileToMessagesDict in structure.items():
            if not await aiofiles.ospath.exists(messageDirectory):
                await aiofiles.os.makedirs(messageDirectory)

            for messageFile, messagesList in messageFileToMessagesDict.items():
                async with aiofiles.open(messageFile, mode = 'a') as file:
                    for message in messagesList:
                        logStatement = self.__getLogStatement(message)
                        await file.write(logStatement)
