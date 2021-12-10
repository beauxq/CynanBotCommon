import json
from datetime import timedelta
from os import path
from typing import Dict

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.chatBand.chatBandInstrument import ChatBandInstrument
    from CynanBotCommon.chatBand.chatBandMember import ChatBandMember
    from CynanBotCommon.timedDict import TimedDict
    from CynanBotCommon.websocketConnectionServer import \
        WebsocketConnectionServer
except:
    import utils
    from timedDict import TimedDict
    from websocketConnectionServer import WebsocketConnectionServer

    from chatBand.chatBandInstrument import ChatBandInstrument
    from chatBand.chatBandMember import ChatBandMember


class ChatBandManager():

    def __init__(
        self,
        websocketConnectionServer: WebsocketConnectionServer,
        chatBandFile: str = 'CynanBotCommon/chatBand/chatBandManager.json',
        eventType: str = 'chatBand',
        eventCooldown: timedelta = timedelta(minutes = 5),
        memberCacheTimeToLive: timedelta = timedelta(minutes = 15)
    ):
        if websocketConnectionServer is None:
            raise ValueError(f'websocketConnectionServer argument is malformed: \"{websocketConnectionServer}\"')
        elif not utils.isValidStr(chatBandFile):
            raise ValueError(f'chatBandFile argument is malformed: \"{chatBandFile}\"')
        elif not utils.isValidStr(eventType):
            raise ValueError(f'eventType argument is malformed: \"{eventType}\"')
        elif eventCooldown is None:
            raise ValueError(f'eventCooldown argument is malformed: \"{eventCooldown}\"')
        elif memberCacheTimeToLive is None:
            raise ValueError(f'memberCacheTimeToLive argument is malformed: \"{memberCacheTimeToLive}\"')

        self.__websocketConnectionServer: WebsocketConnectionServer = websocketConnectionServer
        self.__chatBandFile: str = chatBandFile
        self.__eventType: str = eventType
        self.__lastChatBandMessageTimes: TimedDict = TimedDict(eventCooldown)
        self.__chatBandMemberCache: TimedDict = TimedDict(memberCacheTimeToLive)
        self.__stubChatBandMember: ChatBandMember = ChatBandMember(ChatBandInstrument.BASS, "stub", "stub")

    def clearCaches(self):
        self.__lastChatBandMessageTimes.clear()
        self.__chatBandMemberCache.clear()

    def __findChatBandMember(
        self,
        twitchChannel: str,
        author: str,
        message: str
    ) -> ChatBandMember:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        chatBandMember: ChatBandMember = self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)]

        if chatBandMember is None:
            jsonContents = self.__readJson(twitchChannel)

            if utils.hasItems(jsonContents):
                for key in jsonContents:
                    if key.lower() == author.lower():
                        chatBandMemberJson = jsonContents[key]

                        chatBandMember = ChatBandMember(
                            instrument = ChatBandInstrument.fromStr(utils.getStrFromDict(chatBandMemberJson, 'instrument')),
                            author = key,
                            keyPhrase = utils.getStrFromDict(chatBandMemberJson, 'keyPhrase')
                        )

                        self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)] = chatBandMember
                        break

        if chatBandMember is None:
            self.__chatBandMemberCache[self.__getCooldownKey(twitchChannel, author)] = self.__stubChatBandMember

        if chatBandMember is not None and chatBandMember is not self.__stubChatBandMember and chatBandMember.getKeyPhrase() == message:
            return chatBandMember
        else:
            return None

    def __getCooldownKey(self, twitchChannel: str, author: str) -> str:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')

        return f'{twitchChannel.lower()}:{author.lower()}'

    async def playInstrumentForMessage(self, twitchChannel: str, author: str, message: str) -> bool:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')
        elif not utils.isValidStr(author):
            raise ValueError(f'author argument is malformed: \"{author}\"')
        elif not utils.isValidStr(message):
            raise ValueError(f'message argument is malformed: \"{message}\"')

        chatBandMember = self.__findChatBandMember(
            twitchChannel = twitchChannel,
            author = author,
            message = message
        )

        if chatBandMember is None:
            return False
        elif chatBandMember is self.__stubChatBandMember:
            return False
        elif not self.__lastChatBandMessageTimes.isReadyAndUpdate(self.__getCooldownKey(twitchChannel, author)):
            return False

        await self.__websocketConnectionServer.sendEvent(
            twitchChannel = twitchChannel,
            eventType = self.__eventType,
            eventData = self.__toEventData(chatBandMember)
        )

        return True

    def __readAllJson(self) -> Dict:
        if not path.exists(self.__chatBandFile):
            raise FileNotFoundError(f'Chat Band file not found: \"{self.__chatBandFile}\"')

        with open(self.__chatBandFile, 'r') as file:
            jsonContents = json.load(file)

        if jsonContents is None:
            raise IOError(f'Error reading from Chat Band file: \"{self.__chatBandFile}\"')
        elif len(jsonContents) == 0:
            raise ValueError(f'JSON contents of Chat Band file \"{self.__chatBandFile}\" is empty')

        return jsonContents

    def __readJson(self, twitchChannel: str) -> ChatBandMember:
        if not utils.isValidStr(twitchChannel):
            raise ValueError(f'twitchChannel argument is malformed: \"{twitchChannel}\"')

        jsonContents = self.__readAllJson()
        if not utils.hasItems(jsonContents):
            return None

        for key in jsonContents:
            if key.lower() == twitchChannel.lower():
                return jsonContents[key]

        return None

    def __toEventData(self, chatBandMember: ChatBandMember) -> Dict:
        if chatBandMember is None:
            raise ValueError(f'chatBandMember argument is malformed: \"{chatBandMember}\"')

        return {
            'author': chatBandMember.getAuthor(),
            'keyPhrase': chatBandMember.getKeyPhrase(),
            'instrument': chatBandMember.getInstrument().toStr()
        }
