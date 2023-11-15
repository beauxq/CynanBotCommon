from typing import Any, Dict, Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


# This class intends to directly correspond to Twitch's "Ban User" API:
# https://dev.twitch.tv/docs/api/reference/#ban-user
class TwitchBanRequest():

    def __init__(
        self,
        duration: Optional[int],
        broadcasterUserId: str,
        moderatorUserId: str,
        reason: Optional[str],
        userIdToBan: str
    ):
        if duration is not None and not utils.isValidInt(duration):
            raise ValueError(f'duration argument is malformed: \"{duration}\"')
        elif duration is not None and (duration < 1 or duration > 1209600):
            raise ValueError(f'duration argument is out of bounds: {duration}')
        elif not utils.isValidStr(broadcasterUserId):
            raise ValueError(f'broadcasterUserId argument is malformed: \"{broadcasterUserId}\"')
        elif not utils.isValidStr(moderatorUserId):
            raise ValueError(f'moderatorUserId argument is malformed: \"{moderatorUserId}\"')
        elif reason is not None and not isinstance(reason, str):
            raise ValueError(f'reason argument is malformed: \"{reason}\"')
        elif not utils.isValidStr(userIdToBan):
            raise ValueError(f'userIdToBan argument is malformed: \"{userIdToBan}\"')

        self.__duration: Optional[int] = duration
        self.__broadcasterUserId: str = broadcasterUserId
        self.__moderatorUserId: str = moderatorUserId
        self.__reason: Optional[str] = reason
        self.__userIdToBan: str = userIdToBan

    def getBroadcasterUserId(self) -> str:
        return self.__broadcasterUserId

    def getDuration(self) -> Optional[int]:
        return self.__duration

    def getModeratorUserId(self) -> str:
        return self.__moderatorUserId

    def getReason(self) -> Optional[str]:
        return self.__reason

    def getUserIdToBan(self) -> str:
        return self.__userIdToBan

    def __repr__(self) -> str:
        dictionary = self.toDictionary()
        return str(dictionary)

    def toDictionary(self) -> Dict[str, Any]:
        return {
            'duration': self.__duration,
            'broadcasterUserId': self.__broadcasterUserId,
            'moderatorUserId': self.__moderatorUserId,
            'reason': self.__reason,
            'userIdToBan': self.__userIdToBan
        }

    def toJson(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            'user_id': self.__userIdToBan
        }

        if utils.isValidInt(self.__duration):
            data['duration'] = self.__duration

        if utils.isValidStr(self.__reason):
            data['reason'] = self.__reason

        return {
            'data': data
        }
