from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class TwitchBannedUserRequest():

    def __init__(
        self,
        broadcasterId: str,
        requestedUserId: Optional[str]
    ):
        if not utils.isValidStr(broadcasterId):
            raise ValueError(f'broadcasterId argument is malformed: \"{broadcasterId}\"')
        elif requestedUserId is not None and not isinstance(requestedUserId, str):
            raise ValueError(f'requestedUserId argument is malformed: \"{requestedUserId}\"')

        self.__broadcasterId: str = broadcasterId
        self.__requestedUserId: Optional[str] = requestedUserId

    def getBroadcasterId(self) -> str:
        return self.__broadcasterId

    def getRequestedUserId(self) -> Optional[str]:
        return self.__requestedUserId

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'broadcasterId': self.__broadcasterId,
            'requestedUserId': self.__requestedUserId
        }
