from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
    from CynanBotCommon.simpleDateTime import SimpleDateTime
except:
    import utils
    from simpleDateTime import SimpleDateTime


# This class intends to directly correspond to Twitch's "Ban User" API:
# https://dev.twitch.tv/docs/api/reference/#ban-user
class TwitchBanResponse():

    def __init__(
        self,
        createdAt: SimpleDateTime,
        endTime: Optional[SimpleDateTime],
        broadcasterUserId: str,
        moderatorUserId: str,
        userId: str
    ):
        if not isinstance(createdAt, SimpleDateTime):
            raise ValueError(f'createdAt argument is malformed: \"{createdAt}\"')
        elif endTime is not None and not isinstance(endTime, SimpleDateTime):
            raise ValueError(f'endTime argument is malformed: \"{endTime}\"')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(moderatorUserId):
            raise ValueError(f'moderatorUserId argument is malformed: \"{moderatorUserId}\"')
        elif not utils.isValidStr(userId):
            raise ValueError(f'userId argument is malformed: \"{userId}\"')

        self.__createdAt: SimpleDateTime = createdAt
        self.__endTime: Optional[SimpleDateTime] = endTime
        self.__broadcasterUserId: str = broadcasterUserId
        self.__moderatorUserId: str = moderatorUserId
        self.__userId: str = userId

    def getBroadcasterUserId(self) -> str:
        return self.__broadcasterUserId

    def getCreatedAt(self) -> SimpleDateTime:
        return self.__createdAt

    def getEndTime(self) -> Optional[SimpleDateTime]:
        return self.__endTime

    def getModeratorUserId(self) -> str:
        return self.__moderatorUserId

    def getUserId(self) -> str:
        return self.__userId

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'broadcasterUserId': self.__broadcasterUserId,
            'createdAt': self.__createdAt,
            'endTime': self.__endTime,
            'moderatorUserId': self.__moderatorUserId,
            'userId': self.__userId
        }
