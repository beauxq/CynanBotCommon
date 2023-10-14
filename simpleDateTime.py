from datetime import datetime, timedelta, timezone
from typing import Any, Optional

try:
    import CynanBotCommon.utils as utils
except:
    import utils


class SimpleDateTime():

    def __init__(
        self,
        now: Optional[datetime] = None,
        timeZone: timezone = timezone.utc
    ):
        if now is not None and not isinstance(now, datetime):
            raise ValueError(f'now argument is malformed: \"{now}\"')
        elif not isinstance(timeZone, timezone):
            raise ValueError(f'timeZone argument is malformed: \"{timeZone}\"')

        if now is None:
            self.__now: datetime = datetime.now(timeZone)
        else:
            self.__now: datetime = now

    def __add__(self, other: Any):
        if isinstance(other, SimpleDateTime):
            return self.__now + other.__now
        elif isinstance(other, datetime):
            return self.__now + other
        elif isinstance(other, timedelta):
            return self.__now + other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SimpleDateTime):
            return self.__now == other.__now
        elif isinstance(other, datetime):
            return self.__now == other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def getDateTime(self) -> datetime:
        return self.__now

    def getDateAndTimeStr(self, includeMillis: bool = False) -> str:
        if not utils.isValidBool(includeMillis):
            raise ValueError(f'includeMillis argument is malformed: \"{includeMillis}\"')

        return f'{self.getYearMonthDayStr()} {self.getTimeStr(includeMillis)}'

    def getDayStr(self) -> str:
        return self.__now.strftime('%d')

    def getHourStr(self) -> str:
        return self.__now.strftime('%H')

    def getIsoFormatStr(self) -> str:
        return self.__now.isoformat()

    def getMillisStr(self) -> str:
        return self.__now.strftime('%f')[:-3]

    def getMinuteStr(self) -> str:
        return self.__now.strftime('%M')

    def getMonthStr(self) -> str:
        return self.__now.strftime('%m')

    def getMonthInt(self) -> int:
        return self.__now.month

    def getSecondStr(self) -> str:
        return self.__now.strftime('%S')

    def getTimeStr(self, includeMillis: bool = False) -> str:
        if not utils.isValidBool(includeMillis):
            raise ValueError(f'includeMillis argument is malformed: \"{includeMillis}\"')

        timeStr = f'{self.getHourStr()}:{self.getMinuteStr()}:{self.getSecondStr()}'

        if includeMillis:
            timeStr = f'{timeStr}.{self.getMillisStr()}'

        return timeStr

    def getYearInt(self) -> int:
        return self.__now.year

    def getYearStr(self) -> str:
        return self.__now.strftime('%Y')

    def getYearMonthDayStr(self) -> str:
        return f'{self.getYearStr()}/{self.getMonthStr()}/{self.getDayStr()}'

    def __ge__(self, other: Any) -> bool:
        if isinstance(other, SimpleDateTime):
            return self.__now >= other.__now
        elif isinstance(other, datetime):
            return self.__now >= other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def __gt__(self, other: Any) -> bool:
        if isinstance(other, SimpleDateTime):
            return self.__now > other.__now
        elif isinstance(other, datetime):
            return self.__now > other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def __le__(self, other: Any) -> bool:
        if isinstance(other, SimpleDateTime):
            return self.__now <= other.__now
        elif isinstance(other, datetime):
            return self.__now <= other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def __lt__(self, other: Any) -> bool:
        if isinstance(other, SimpleDateTime):
            return self.__now < other.__now
        elif isinstance(other, datetime):
            return self.__now < other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')

    def __str__(self) -> str:
        return f'{self.__now}'

    def __sub__(self, other: Any):
        if isinstance(other, SimpleDateTime):
            return self.__now - other.__now
        elif isinstance(other, datetime):
            return self.__now - other
        elif isinstance(other, timedelta):
            return self.__now - other
        else:
            raise ValueError(f'`other` is an unsupported type: \"{other}\"')
