from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
    from CynanBotCommon.twitch.websocket.websocketMessageType import \
        WebsocketMessageType
    from CynanBotCommon.twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType
except:
    import utils
    from simpleDateTime import SimpleDateTime

    from twitch.websocket.websocketMessageType import WebsocketMessageType
    from twitch.websocket.websocketSubscriptionType import \
        WebsocketSubscriptionType


class WebsocketMetadata():

    def __init__(
        self,
        messageTimestamp: SimpleDateTime,
        messageId: str,
        subscriptionVersion: Optional[str],
        messageType: WebsocketMessageType,
        subscriptionType: Optional[WebsocketSubscriptionType]
    ):
        if not isinstance(messageTimestamp, SimpleDateTime):
            raise ValueError(f'messageTimestamp argument is malformed: \"{messageTimestamp}\"')
        elif not utils.isValidStr(messageId):
            raise ValueError(f'messageId argument is malformed: \"{messageId}\"')
        elif subscriptionVersion is not None and not utils.isValidStr(subscriptionVersion):
            raise ValueError(f'subscriptionVersion argument is malformed: \"{subscriptionVersion}\"')
        elif not isinstance(messageType, WebsocketMessageType):
            raise ValueError(f'messageType argument is malformed: \"{messageType}\"')
        elif subscriptionType is not None and not isinstance(subscriptionType, WebsocketSubscriptionType):
            raise ValueError(f'subscriptionType argument is malformed: \"{subscriptionType}\"')

        self.__messageTimestamp: SimpleDateTime = messageTimestamp
        self.__messageId: str = messageId
        self.__subscriptionVersion: Optional[str] = subscriptionVersion
        self.__messageType: WebsocketMessageType = messageType
        self.__subscriptionType: Optional[WebsocketSubscriptionType] = subscriptionType

    def getMessageId(self) -> str:
        return self.__messageId

    def getMessageTimestamp(self) -> SimpleDateTime:
        return self.__messageTimestamp

    def getMessageType(self) -> WebsocketMessageType:
        return self.__messageType

    def getSubscriptionType(self) -> Optional[WebsocketSubscriptionType]:
        return self.__subscriptionType

    def getSubscriptionVersion(self) -> Optional[str]:
        return self.__subscriptionVersion

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'messageId': self.__messageId,
            'messageTimestamp': self.__messageTimestamp,
            'messageType': self.__messageType,
            'subscriptionType': self.__subscriptionType,
            'subscriptionVersion': self.__subscriptionVersion
        }
